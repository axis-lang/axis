// rustimport:pyo3
//d: axis.pest

use from_pest::FromPest;
use pyo3::prelude::*;

// #[macro_use]
// extern crate pest_derive;
extern crate from_pest;

//#[macro_use]
//extern crate pest_ast;
// extern crate pest;

use pest_ast::FromPest;

use pest::{Parser, Span};
use pest_derive::Parser;

#[derive(Parser)]
#[grammar = "axis.pest"]
pub struct AxisParser;

fn span_into_string(span: Span) -> String {
    span.as_str().into()
}

#[derive(Debug, FromPest)]
#[pest_ast(rule(Rule::Id))]
struct Id(#[pest_ast(inner(with(span_into_string)))] String);

#[pyfunction]
pub fn parse_type_expr(input: String) -> PyResult<String> {
    let result = AxisParser::parse(Rule::Expr, input.as_str());

    if let Result::Err(e) = result {
        return PyResult::Err(PyErr::new::<pyo3::exceptions::PySyntaxError, _>(format!(
            "{}",
            e
        )));
    }

    let tokens = result.unwrap().flatten().collect::<Vec<_>>();

    println!("{:?}", tokens);

    return PyResult::Ok(input);
}

// Uncomment the below to implement custom pyo3 binding code. Otherwise,
// rustimport will generate it for you for all functions annotated with
// #[pyfunction] and all structs annotated with #[pyclass].
//
//#[pymodule]
//fn parser(_py: Python, m: &PyModule) -> PyResult<()> {
//    m.add_function(wrap_pyfunction!(say_hello, m)?)?;
//    Ok(())
//}
