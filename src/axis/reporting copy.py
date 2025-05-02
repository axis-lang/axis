#%%
from enum import Enum, auto
from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from rich.console import Console
from rich.style import Style
from rich.text import Text

# Reconstrucción de la representación de spans al estilo Codespan Reporting

class Severity(Enum):
    ERROR = auto()
    WARNING = auto()
    NOTE = auto()

_SEVERITY_STYLES = {
    Severity.ERROR: Style(color="red", bold=True),
    Severity.WARNING: Style(color="yellow", bold=True),
    Severity.NOTE: Style(color="blue", bold=True),
}

class LabelStyle(Enum):
    PRIMARY = auto()
    SECONDARY = auto()

_LABEL_STYLES = {
    LabelStyle.PRIMARY: Style(color="red", bold=True),
    LabelStyle.SECONDARY: Style(color="blue", bold=True),
}

@dataclass
class Label:
    file_id: int
    range: Tuple[int, int]  # (start_offset, end_offset)
    message: str = ""
    style: LabelStyle = LabelStyle.PRIMARY

@dataclass
class Diagnostic:
    severity: Severity
    code: str
    message: str
    labels: List[Label] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    suggestion: Optional[str] = None

class Files:
    def add(self, name: str, source: str) -> int:
        raise NotImplementedError
    def get(self, file_id: int) -> Tuple[str, str]:
        raise NotImplementedError

@dataclass
class SimpleFile:
    name: str
    source: str
    line_starts: List[int] = field(init=False)

    def __post_init__(self):
        # calcular índices de inicio de línea
        self.line_starts = [0]
        for i, ch in enumerate(self.source):
            if ch == '\n':
                self.line_starts.append(i + 1)

    def linecol(self, pos: int) -> Tuple[int, int]:
        # convertir offset a (línea, columna)
        for idx, start in enumerate(self.line_starts):
            end = self.line_starts[idx + 1] if idx + 1 < len(self.line_starts) else len(self.source)
            if start <= pos < end:
                return idx + 1, pos - start + 1
        return len(self.line_starts), pos - self.line_starts[-1] + 1

    def slice_lines(self, start_line: int, end_line: int) -> List[str]:
        # extraer texto de líneas [start_line..end_line]
        lines = []
        for ln in range(start_line, end_line + 1):
            s = self.line_starts[ln - 1]
            e = self.line_starts[ln] if ln < len(self.line_starts) else len(self.source)
            lines.append(self.source[s:e].rstrip('\n'))
        return lines

class SimpleFiles(Files):
    def __init__(self):
        self.files: List[SimpleFile] = []

    def add(self, name: str, source: str) -> int:
        f = SimpleFile(name, source)
        self.files.append(f)
        return len(self.files) - 1

    def get(self, file_id: int) -> Tuple[str, str]:
        f = self.files[file_id]
        return f.name, f.source

    def file_obj(self, file_id: int) -> SimpleFile:
        return self.files[file_id]

class Reporter:
    def __init__(self, files: SimpleFiles, console: Optional[Console] = None):
        self.files = files
        self.console = console or Console()

    def emit(self, diagnostic: Diagnostic):
        report = Text()
        # Cabecera al estilo Codespan
        hdr = Text(f"{diagnostic.severity.name.lower()}[{diagnostic.code}]: {diagnostic.message}\n")
        hdr.stylize(_SEVERITY_STYLES[diagnostic.severity])
        report.append(hdr)

        for lbl in diagnostic.labels:
            name, _ = self.files.get(lbl.file_id)
            f = self.files.file_obj(lbl.file_id)
            start, end = lbl.range
            sl, sc = f.linecol(start)
            # imprimir ubicación
            loc = Text(f" --> {name}:{sl}:{sc}\n", style="dim")
            report.append(loc)

            # Extraer una sola línea de contexto
            line = f.slice_lines(sl, sl)[0]
            gutter = f" {sl} | "
            report.append(Text(gutter + line + "\n"))

            # marcador con tildes ~ como Codespan
            prefix = " " * (len(gutter) + sc - 1)
            length = max(1, end - start)
            underline = Text(prefix + "~" * length)
            underline.stylize(_LABEL_STYLES[lbl.style])
            if lbl.message:
                underline.append(f" {lbl.message}")
            underline.append("\n")
            report.append(underline)

        # notas y sugerencia
        for note in diagnostic.notes:
            nt = Text(f"note: {note}\n")
            nt.stylize("italic")
            report.append(nt)
        if diagnostic.suggestion:
            sg = Text(f"suggestion: {diagnostic.suggestion}\n")
            sg.stylize("underline")
            report.append(sg)

        # salida única
        self.console.print(report)

# ===== TESTING CODE =====
if __name__ == "__main__":
    console = Console()
    files = SimpleFiles()

    # Test básico de línea única y etiqueta primaria
    src = (
        "fn main() {\n"
        "    let x = 10;\n"
        "    let y = x + ;\n"
        "}\n"
    )
    fid = files.add("test.rs", src)
    pos = src.find("+ ;")
    diag1 = Diagnostic(
        severity=Severity.ERROR,
        code="E001",
        message="Syntax error",
        labels=[Label(fid, (pos, pos+2), "expected expression")]
    )
    Reporter(files, console).emit(diag1)

    # Test secundario con nota y sugerencia
    start = src.find("let x")
    end = src.find("y =") + 1
    diag2 = Diagnostic(
        severity=Severity.WARNING,
        code="W123",
        message="Refactor suggestion",
        labels=[Label(fid, (start, end), "simplify assignment", LabelStyle.SECONDARY)],
        notes=["span reducido a una línea"],
        suggestion="Remove trailing semicolon."
    )
    Reporter(files, console).emit(diag2)

    # Test complejo con múltiples labels y líneas
    src2 = (
        "pub fn calc(a: i32, b: i32) -> i32 {\n"
        "    let sum = a + b;\n"
        "    let product = a * b;\n"
        "    if sum + product > 100 {\n"
        "        panic!(\"Value {} too large\", sum + product);\n"
        "    }\n"
        "    sum - product\n"
        "}\n"
    )
    fid2 = files.add("calc.rs", src2)
    # Labels múltiples: uno primario y uno secundario
    start1 = src2.find("sum = a + b")
    end1 = start1 + len("sum = a + b")
    start2 = src2.find("product = a * b")
    end2 = start2 + len("product = a * b")
    diag3 = Diagnostic(
        severity=Severity.ERROR,
        code="E042",
        message="Calculation overflow",
        labels=[
            Label(fid2, (start1, end1), "check addition", LabelStyle.PRIMARY),
            Label(fid2, (start2, end2), "check multiplication", LabelStyle.SECONDARY),
        ],
        notes=["Potential overflow in arithmetic operations."],
        suggestion="Use checked_add and checked_mul methods."
    )
    Reporter(files, console).emit(diag3)
