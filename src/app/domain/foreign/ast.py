from __future__ import annotations

from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, RootModel


# ── Node kinds ──────────────────────────────────────────────────────────────────


class NodeKind(StrEnum):
    LOAD = "Load"
    STORE = "Store"
    DEL = "Del"
    ADD = "Add"
    SUB = "Sub"
    MULT = "Mult"
    MAT_MULT = "MatMult"
    DIV = "Div"
    MOD = "Mod"
    POW = "Pow"
    L_SHIFT = "LShift"
    R_SHIFT = "RShift"
    BIT_OR = "BitOr"
    BIT_XOR = "BitXor"
    BIT_AND = "BitAnd"
    FLOOR_DIV = "FloorDiv"
    AND = "And"
    OR = "Or"
    INVERT = "Invert"
    NOT = "Not"
    U_ADD = "UAdd"
    U_SUB = "USub"
    EQ = "Eq"
    NOT_EQ = "NotEq"
    LT = "Lt"
    LT_E = "LtE"
    GT = "Gt"
    GT_E = "GtE"
    IS = "Is"
    IS_NOT = "IsNot"
    IN = "In"
    NOT_IN = "NotIn"
    ARG = "arg"
    ARGUMENTS = "arguments"
    KEYWORD = "keyword"
    ALIAS = "alias"
    COMPREHENSION = "comprehension"
    WITHITEM = "withitem"
    EXCEPT_HANDLER = "ExceptHandler"
    ATTRIBUTE = "Attribute"
    AWAIT = "Await"
    BIN_OP = "BinOp"
    BOOL_OP = "BoolOp"
    CALL = "Call"
    COMPARE = "Compare"
    CONSTANT = "Constant"
    DICT = "Dict"
    DICT_COMP = "DictComp"
    FORMATTED_VALUE = "FormattedValue"
    GENERATOR_EXP = "GeneratorExp"
    IF_EXP = "IfExp"
    JOINED_STR = "JoinedStr"
    LAMBDA = "Lambda"
    LIST = "List"
    LIST_COMP = "ListComp"
    NAME = "Name"
    NAMED_EXPR = "NamedExpr"
    SET = "Set"
    SET_COMP = "SetComp"
    SLICE = "Slice"
    STARRED = "Starred"
    SUBSCRIPT = "Subscript"
    TUPLE = "Tuple"
    UNARY_OP = "UnaryOp"
    YIELD = "Yield"
    YIELD_FROM = "YieldFrom"
    TYPE_VAR = "TypeVar"
    PARAM_SPEC = "ParamSpec"
    TYPE_VAR_TUPLE = "TypeVarTuple"
    MATCH_VALUE = "MatchValue"
    MATCH_SINGLETON = "MatchSingleton"
    MATCH_SEQUENCE = "MatchSequence"
    MATCH_MAPPING = "MatchMapping"
    MATCH_CLASS = "MatchClass"
    MATCH_STAR = "MatchStar"
    MATCH_AS = "MatchAs"
    MATCH_OR = "MatchOr"
    MATCH_CASE = "match_case"
    ANN_ASSIGN = "AnnAssign"
    ASSERT = "Assert"
    ASSIGN = "Assign"
    ASYNC_FOR = "AsyncFor"
    ASYNC_FUNCTION_DEF = "AsyncFunctionDef"
    ASYNC_WITH = "AsyncWith"
    AUG_ASSIGN = "AugAssign"
    BREAK = "Break"
    CLASS_DEF = "ClassDef"
    CONTINUE = "Continue"
    DELETE = "Delete"
    EXPR = "Expr"
    FOR = "For"
    FUNCTION_DEF = "FunctionDef"
    GLOBAL = "Global"
    IF = "If"
    IMPORT = "Import"
    IMPORT_FROM = "ImportFrom"
    NONLOCAL = "Nonlocal"
    PASS = "Pass"
    RAISE = "Raise"
    RETURN = "Return"
    TRY = "Try"
    MATCH = "Match"
    TRY_STAR = "TryStar"
    TYPE_ALIAS = "TypeAlias"
    WHILE = "While"
    WITH = "With"
    MODULE = "Module"


# ── Scalars ─────────────────────────────────────────────────────────────────────


class Line(RootModel[int], frozen=True):
    root: int = Field(ge=1)


class Column(RootModel[int], frozen=True):
    root: int = Field(ge=0)


class Identifier(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class ModulePath(RootModel[str], frozen=True):
    root: str = Field(min_length=1)


class ConstantKind(RootModel[str], frozen=True):
    """A `Constant`'s string-prefix marker, `u` for a `u"..."` literal. Present only when the literal
    carried a prefix, so it is paired with `Absent` for the bare constant."""

    root: str = Field(min_length=1)


class ImportLevel(RootModel[int], frozen=True):
    """An `ImportFrom`'s leading-dot count: 0 is absolute, n is n dots. Unbounded on purpose: the dot
    count is open, so the open range is the domain fact."""

    root: int = Field(ge=0)


class Conversion(RootModel[Literal[-1, 97, 114, 115]], frozen=True):
    """A `FormattedValue`'s conversion code: -1 none, 115 `!s`, 114 `!r`, 97 `!a`. The compiler's own
    closed set of conversion codes."""

    root: Literal[-1, 97, 114, 115]


class Simple(RootModel[Literal[0, 1]], frozen=True):
    """An `AnnAssign`'s simple flag: 1 when the target is a bare `Name`, 0 otherwise."""

    root: Literal[0, 1]


class IsAsync(RootModel[Literal[0, 1]], frozen=True):
    """A `comprehension`'s async flag: 1 for `async for`, 0 otherwise."""

    root: Literal[0, 1]


class LiteralValue(RootModel[bool | int | float | str | None], frozen=True):
    """A `Constant`'s value as ast2json emits it: `bool`, `int`, `float`, `str`, or `null`. The converter
    renders `complex`, `bytes`, and the `Ellipsis` literal `...` as their `str` forms, so `str` carries
    them, and `None` is the literal `None` constant, never an omitted field."""

    root: bool | int | float | str | None


class Absent(RootModel[None], frozen=True):
    """An optional foreign field the compiler sent as `null`: the named variant of omission, so bare
    `None` never crosses the boundary."""

    root: None


class AstNode(BaseModel):
    model_config = ConfigDict(frozen=True, extra="ignore")


# ── Expression contexts ─────────────────────────────────────────────────────────


class Load(AstNode):
    node_type: Literal[NodeKind.LOAD] = Field(default=NodeKind.LOAD, alias="_type")


class Store(AstNode):
    node_type: Literal[NodeKind.STORE] = Field(default=NodeKind.STORE, alias="_type")


class Del(AstNode):
    node_type: Literal[NodeKind.DEL] = Field(default=NodeKind.DEL, alias="_type")


ExprContext = Annotated[Load | Store | Del, Field(discriminator="node_type")]


# ── Operators ───────────────────────────────────────────────────────────────────


class Add(AstNode):
    node_type: Literal[NodeKind.ADD] = Field(default=NodeKind.ADD, alias="_type")


class Sub(AstNode):
    node_type: Literal[NodeKind.SUB] = Field(default=NodeKind.SUB, alias="_type")


class Mult(AstNode):
    node_type: Literal[NodeKind.MULT] = Field(default=NodeKind.MULT, alias="_type")


class MatMult(AstNode):
    node_type: Literal[NodeKind.MAT_MULT] = Field(default=NodeKind.MAT_MULT, alias="_type")


class Div(AstNode):
    node_type: Literal[NodeKind.DIV] = Field(default=NodeKind.DIV, alias="_type")


class Mod(AstNode):
    node_type: Literal[NodeKind.MOD] = Field(default=NodeKind.MOD, alias="_type")


class Pow(AstNode):
    node_type: Literal[NodeKind.POW] = Field(default=NodeKind.POW, alias="_type")


class LShift(AstNode):
    node_type: Literal[NodeKind.L_SHIFT] = Field(default=NodeKind.L_SHIFT, alias="_type")


class RShift(AstNode):
    node_type: Literal[NodeKind.R_SHIFT] = Field(default=NodeKind.R_SHIFT, alias="_type")


class BitOr(AstNode):
    node_type: Literal[NodeKind.BIT_OR] = Field(default=NodeKind.BIT_OR, alias="_type")


class BitXor(AstNode):
    node_type: Literal[NodeKind.BIT_XOR] = Field(default=NodeKind.BIT_XOR, alias="_type")


class BitAnd(AstNode):
    node_type: Literal[NodeKind.BIT_AND] = Field(default=NodeKind.BIT_AND, alias="_type")


class FloorDiv(AstNode):
    node_type: Literal[NodeKind.FLOOR_DIV] = Field(default=NodeKind.FLOOR_DIV, alias="_type")


Operator = Annotated[
    Add | Sub | Mult | MatMult | Div | Mod | Pow | LShift | RShift | BitOr | BitXor | BitAnd | FloorDiv,
    Field(discriminator="node_type"),
]


# ── Boolean and unary operators ─────────────────────────────────────────────────


class And(AstNode):
    node_type: Literal[NodeKind.AND] = Field(default=NodeKind.AND, alias="_type")


class Or(AstNode):
    node_type: Literal[NodeKind.OR] = Field(default=NodeKind.OR, alias="_type")


BoolOp_ = Annotated[And | Or, Field(discriminator="node_type")]


class Invert(AstNode):
    node_type: Literal[NodeKind.INVERT] = Field(default=NodeKind.INVERT, alias="_type")


class Not(AstNode):
    node_type: Literal[NodeKind.NOT] = Field(default=NodeKind.NOT, alias="_type")


class UAdd(AstNode):
    node_type: Literal[NodeKind.U_ADD] = Field(default=NodeKind.U_ADD, alias="_type")


class USub(AstNode):
    node_type: Literal[NodeKind.U_SUB] = Field(default=NodeKind.U_SUB, alias="_type")


UnaryOperator = Annotated[Invert | Not | UAdd | USub, Field(discriminator="node_type")]


# ── Comparison operators ────────────────────────────────────────────────────────


class Eq(AstNode):
    node_type: Literal[NodeKind.EQ] = Field(default=NodeKind.EQ, alias="_type")


class NotEq(AstNode):
    node_type: Literal[NodeKind.NOT_EQ] = Field(default=NodeKind.NOT_EQ, alias="_type")


class Lt(AstNode):
    node_type: Literal[NodeKind.LT] = Field(default=NodeKind.LT, alias="_type")


class LtE(AstNode):
    node_type: Literal[NodeKind.LT_E] = Field(default=NodeKind.LT_E, alias="_type")


class Gt(AstNode):
    node_type: Literal[NodeKind.GT] = Field(default=NodeKind.GT, alias="_type")


class GtE(AstNode):
    node_type: Literal[NodeKind.GT_E] = Field(default=NodeKind.GT_E, alias="_type")


class Is(AstNode):
    node_type: Literal[NodeKind.IS] = Field(default=NodeKind.IS, alias="_type")


class IsNot(AstNode):
    node_type: Literal[NodeKind.IS_NOT] = Field(default=NodeKind.IS_NOT, alias="_type")


class In(AstNode):
    node_type: Literal[NodeKind.IN] = Field(default=NodeKind.IN, alias="_type")


class NotIn(AstNode):
    node_type: Literal[NodeKind.NOT_IN] = Field(default=NodeKind.NOT_IN, alias="_type")


CmpOp = Annotated[
    Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn, Field(discriminator="node_type")
]


# ── Helper nodes ────────────────────────────────────────────────────────────────


class Arg(AstNode):
    node_type: Literal[NodeKind.ARG] = Field(default=NodeKind.ARG, alias="_type")
    lineno: Line
    col_offset: Column
    arg: Identifier
    annotation: Expression | Absent


class Arguments(AstNode):
    node_type: Literal[NodeKind.ARGUMENTS] = Field(default=NodeKind.ARGUMENTS, alias="_type")
    posonlyargs: tuple[Arg, ...]
    args: tuple[Arg, ...]
    vararg: Arg | Absent
    kwonlyargs: tuple[Arg, ...]
    kw_defaults: tuple[Expression | Absent, ...]
    kwarg: Arg | Absent
    defaults: tuple[Expression, ...]


class Keyword(AstNode):
    node_type: Literal[NodeKind.KEYWORD] = Field(default=NodeKind.KEYWORD, alias="_type")
    lineno: Line
    col_offset: Column
    arg: Identifier | Absent
    value: Expression


class Alias(AstNode):
    node_type: Literal[NodeKind.ALIAS] = Field(default=NodeKind.ALIAS, alias="_type")
    lineno: Line
    col_offset: Column
    name: ModulePath
    asname: Identifier | Absent


class Comprehension(AstNode):
    node_type: Literal[NodeKind.COMPREHENSION] = Field(default=NodeKind.COMPREHENSION, alias="_type")
    target: Expression
    iter: Expression
    ifs: tuple[Expression, ...]
    is_async: IsAsync


class Withitem(AstNode):
    node_type: Literal[NodeKind.WITHITEM] = Field(default=NodeKind.WITHITEM, alias="_type")
    context_expr: Expression
    optional_vars: Expression | Absent


class ExceptHandler(AstNode):
    node_type: Literal[NodeKind.EXCEPT_HANDLER] = Field(default=NodeKind.EXCEPT_HANDLER, alias="_type")
    lineno: Line
    col_offset: Column
    type: Expression | Absent
    name: Identifier | Absent
    body: tuple[Statement, ...]


# ── Expressions ─────────────────────────────────────────────────────────────────


class Attribute(AstNode):
    node_type: Literal[NodeKind.ATTRIBUTE] = Field(default=NodeKind.ATTRIBUTE, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression
    attr: Identifier
    ctx: ExprContext


class Await(AstNode):
    node_type: Literal[NodeKind.AWAIT] = Field(default=NodeKind.AWAIT, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression


class BinOp(AstNode):
    node_type: Literal[NodeKind.BIN_OP] = Field(default=NodeKind.BIN_OP, alias="_type")
    lineno: Line
    col_offset: Column
    left: Expression
    op: Operator
    right: Expression


class BoolOp(AstNode):
    node_type: Literal[NodeKind.BOOL_OP] = Field(default=NodeKind.BOOL_OP, alias="_type")
    lineno: Line
    col_offset: Column
    op: BoolOp_
    values: tuple[Expression, ...]


class Call(AstNode):
    node_type: Literal[NodeKind.CALL] = Field(default=NodeKind.CALL, alias="_type")
    lineno: Line
    col_offset: Column
    func: Expression
    args: tuple[Expression, ...]
    keywords: tuple[Keyword, ...]


class Compare(AstNode):
    node_type: Literal[NodeKind.COMPARE] = Field(default=NodeKind.COMPARE, alias="_type")
    lineno: Line
    col_offset: Column
    left: Expression
    ops: tuple[CmpOp, ...]
    comparators: tuple[Expression, ...]


class Constant(AstNode):
    node_type: Literal[NodeKind.CONSTANT] = Field(default=NodeKind.CONSTANT, alias="_type")
    lineno: Line
    col_offset: Column
    value: LiteralValue
    kind: ConstantKind | Absent


class Dict(AstNode):
    node_type: Literal[NodeKind.DICT] = Field(default=NodeKind.DICT, alias="_type")
    lineno: Line
    col_offset: Column
    keys: tuple[Expression | Absent, ...]
    values: tuple[Expression, ...]


class DictComp(AstNode):
    node_type: Literal[NodeKind.DICT_COMP] = Field(default=NodeKind.DICT_COMP, alias="_type")
    lineno: Line
    col_offset: Column
    key: Expression
    value: Expression
    generators: tuple[Comprehension, ...]


class FormattedValue(AstNode):
    node_type: Literal[NodeKind.FORMATTED_VALUE] = Field(default=NodeKind.FORMATTED_VALUE, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression
    conversion: Conversion
    format_spec: Expression | Absent


class GeneratorExp(AstNode):
    node_type: Literal[NodeKind.GENERATOR_EXP] = Field(default=NodeKind.GENERATOR_EXP, alias="_type")
    lineno: Line
    col_offset: Column
    elt: Expression
    generators: tuple[Comprehension, ...]


class IfExp(AstNode):
    node_type: Literal[NodeKind.IF_EXP] = Field(default=NodeKind.IF_EXP, alias="_type")
    lineno: Line
    col_offset: Column
    test: Expression
    body: Expression
    orelse: Expression


class JoinedStr(AstNode):
    node_type: Literal[NodeKind.JOINED_STR] = Field(default=NodeKind.JOINED_STR, alias="_type")
    lineno: Line
    col_offset: Column
    values: tuple[Expression, ...]


class Lambda(AstNode):
    node_type: Literal[NodeKind.LAMBDA] = Field(default=NodeKind.LAMBDA, alias="_type")
    lineno: Line
    col_offset: Column
    args: Arguments
    body: Expression


class ListExpr(AstNode):
    node_type: Literal[NodeKind.LIST] = Field(default=NodeKind.LIST, alias="_type")
    lineno: Line
    col_offset: Column
    elts: tuple[Expression, ...]
    ctx: ExprContext


class ListComp(AstNode):
    node_type: Literal[NodeKind.LIST_COMP] = Field(default=NodeKind.LIST_COMP, alias="_type")
    lineno: Line
    col_offset: Column
    elt: Expression
    generators: tuple[Comprehension, ...]


class Name(AstNode):
    node_type: Literal[NodeKind.NAME] = Field(default=NodeKind.NAME, alias="_type")
    lineno: Line
    col_offset: Column
    id: Identifier
    ctx: ExprContext


class NamedExpr(AstNode):
    node_type: Literal[NodeKind.NAMED_EXPR] = Field(default=NodeKind.NAMED_EXPR, alias="_type")
    lineno: Line
    col_offset: Column
    target: Expression
    value: Expression


class SetExpr(AstNode):
    node_type: Literal[NodeKind.SET] = Field(default=NodeKind.SET, alias="_type")
    lineno: Line
    col_offset: Column
    elts: tuple[Expression, ...]


class SetComp(AstNode):
    node_type: Literal[NodeKind.SET_COMP] = Field(default=NodeKind.SET_COMP, alias="_type")
    lineno: Line
    col_offset: Column
    elt: Expression
    generators: tuple[Comprehension, ...]


class Slice(AstNode):
    node_type: Literal[NodeKind.SLICE] = Field(default=NodeKind.SLICE, alias="_type")
    lineno: Line
    col_offset: Column
    lower: Expression | Absent
    upper: Expression | Absent
    step: Expression | Absent


class Starred(AstNode):
    node_type: Literal[NodeKind.STARRED] = Field(default=NodeKind.STARRED, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression
    ctx: ExprContext


class Subscript(AstNode):
    node_type: Literal[NodeKind.SUBSCRIPT] = Field(default=NodeKind.SUBSCRIPT, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression
    slice: Expression
    ctx: ExprContext


class TupleExpr(AstNode):
    node_type: Literal[NodeKind.TUPLE] = Field(default=NodeKind.TUPLE, alias="_type")
    lineno: Line
    col_offset: Column
    elts: tuple[Expression, ...]
    ctx: ExprContext


class UnaryOp(AstNode):
    node_type: Literal[NodeKind.UNARY_OP] = Field(default=NodeKind.UNARY_OP, alias="_type")
    lineno: Line
    col_offset: Column
    op: UnaryOperator
    operand: Expression


class Yield(AstNode):
    node_type: Literal[NodeKind.YIELD] = Field(default=NodeKind.YIELD, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression | Absent


class YieldFrom(AstNode):
    node_type: Literal[NodeKind.YIELD_FROM] = Field(default=NodeKind.YIELD_FROM, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression


Expression = Annotated[
    Attribute
    | Await
    | BinOp
    | BoolOp
    | Call
    | Compare
    | Constant
    | Dict
    | DictComp
    | FormattedValue
    | GeneratorExp
    | IfExp
    | JoinedStr
    | Lambda
    | ListExpr
    | ListComp
    | Name
    | NamedExpr
    | SetExpr
    | SetComp
    | Slice
    | Starred
    | Subscript
    | TupleExpr
    | UnaryOp
    | Yield
    | YieldFrom,
    Field(discriminator="node_type"),
]


# ── Type parameters (PEP 695) ───────────────────────────────────────────────────


class TypeVar(AstNode):
    node_type: Literal[NodeKind.TYPE_VAR] = Field(default=NodeKind.TYPE_VAR, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier
    bound: Expression | Absent
    default_value: Expression | Absent


class ParamSpec(AstNode):
    node_type: Literal[NodeKind.PARAM_SPEC] = Field(default=NodeKind.PARAM_SPEC, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier
    default_value: Expression | Absent


class TypeVarTuple(AstNode):
    node_type: Literal[NodeKind.TYPE_VAR_TUPLE] = Field(default=NodeKind.TYPE_VAR_TUPLE, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier
    default_value: Expression | Absent


TypeParam = Annotated[TypeVar | ParamSpec | TypeVarTuple, Field(discriminator="node_type")]


# ── Match patterns (PEP 634) ────────────────────────────────────────────────────


class MatchValue(AstNode):
    node_type: Literal[NodeKind.MATCH_VALUE] = Field(default=NodeKind.MATCH_VALUE, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression


class MatchSingleton(AstNode):
    node_type: Literal[NodeKind.MATCH_SINGLETON] = Field(default=NodeKind.MATCH_SINGLETON, alias="_type")
    lineno: Line
    col_offset: Column
    value: LiteralValue


class MatchSequence(AstNode):
    node_type: Literal[NodeKind.MATCH_SEQUENCE] = Field(default=NodeKind.MATCH_SEQUENCE, alias="_type")
    lineno: Line
    col_offset: Column
    patterns: tuple[Pattern, ...]


class MatchMapping(AstNode):
    node_type: Literal[NodeKind.MATCH_MAPPING] = Field(default=NodeKind.MATCH_MAPPING, alias="_type")
    lineno: Line
    col_offset: Column
    keys: tuple[Expression, ...]
    patterns: tuple[Pattern, ...]
    rest: Identifier | Absent


class MatchClass(AstNode):
    node_type: Literal[NodeKind.MATCH_CLASS] = Field(default=NodeKind.MATCH_CLASS, alias="_type")
    lineno: Line
    col_offset: Column
    cls: Expression
    patterns: tuple[Pattern, ...]
    kwd_attrs: tuple[Identifier, ...]
    kwd_patterns: tuple[Pattern, ...]


class MatchStar(AstNode):
    node_type: Literal[NodeKind.MATCH_STAR] = Field(default=NodeKind.MATCH_STAR, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier | Absent


class MatchAs(AstNode):
    node_type: Literal[NodeKind.MATCH_AS] = Field(default=NodeKind.MATCH_AS, alias="_type")
    lineno: Line
    col_offset: Column
    pattern: Pattern | Absent
    name: Identifier | Absent


class MatchOr(AstNode):
    node_type: Literal[NodeKind.MATCH_OR] = Field(default=NodeKind.MATCH_OR, alias="_type")
    lineno: Line
    col_offset: Column
    patterns: tuple[Pattern, ...]


Pattern = Annotated[
    MatchValue
    | MatchSingleton
    | MatchSequence
    | MatchMapping
    | MatchClass
    | MatchStar
    | MatchAs
    | MatchOr,
    Field(discriminator="node_type"),
]


class MatchCase(AstNode):
    node_type: Literal[NodeKind.MATCH_CASE] = Field(default=NodeKind.MATCH_CASE, alias="_type")
    pattern: Pattern
    guard: Expression | Absent
    body: tuple[Statement, ...]


# ── Statements ──────────────────────────────────────────────────────────────────


class AnnAssign(AstNode):
    node_type: Literal[NodeKind.ANN_ASSIGN] = Field(default=NodeKind.ANN_ASSIGN, alias="_type")
    lineno: Line
    col_offset: Column
    target: Expression
    annotation: Expression
    value: Expression | Absent
    simple: Simple


class Assert(AstNode):
    node_type: Literal[NodeKind.ASSERT] = Field(default=NodeKind.ASSERT, alias="_type")
    lineno: Line
    col_offset: Column
    test: Expression
    msg: Expression | Absent


class Assign(AstNode):
    node_type: Literal[NodeKind.ASSIGN] = Field(default=NodeKind.ASSIGN, alias="_type")
    lineno: Line
    col_offset: Column
    targets: tuple[Expression, ...]
    value: Expression


class AsyncFor(AstNode):
    node_type: Literal[NodeKind.ASYNC_FOR] = Field(default=NodeKind.ASYNC_FOR, alias="_type")
    lineno: Line
    col_offset: Column
    target: Expression
    iter: Expression
    body: tuple[Statement, ...]
    orelse: tuple[Statement, ...]


class AsyncFunctionDef(AstNode):
    node_type: Literal[NodeKind.ASYNC_FUNCTION_DEF] = Field(default=NodeKind.ASYNC_FUNCTION_DEF, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier
    args: Arguments
    body: tuple[Statement, ...]
    decorator_list: tuple[Expression, ...]
    returns: Expression | Absent
    type_params: tuple[TypeParam, ...]


class AsyncWith(AstNode):
    node_type: Literal[NodeKind.ASYNC_WITH] = Field(default=NodeKind.ASYNC_WITH, alias="_type")
    lineno: Line
    col_offset: Column
    items: tuple[Withitem, ...]
    body: tuple[Statement, ...]


class AugAssign(AstNode):
    node_type: Literal[NodeKind.AUG_ASSIGN] = Field(default=NodeKind.AUG_ASSIGN, alias="_type")
    lineno: Line
    col_offset: Column
    target: Expression
    op: Operator
    value: Expression


class Break(AstNode):
    node_type: Literal[NodeKind.BREAK] = Field(default=NodeKind.BREAK, alias="_type")
    lineno: Line
    col_offset: Column


class ClassDef(AstNode):
    node_type: Literal[NodeKind.CLASS_DEF] = Field(default=NodeKind.CLASS_DEF, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier
    bases: tuple[Expression, ...]
    keywords: tuple[Keyword, ...]
    body: tuple[Statement, ...]
    decorator_list: tuple[Expression, ...]
    type_params: tuple[TypeParam, ...]


class Continue(AstNode):
    node_type: Literal[NodeKind.CONTINUE] = Field(default=NodeKind.CONTINUE, alias="_type")
    lineno: Line
    col_offset: Column


class Delete(AstNode):
    node_type: Literal[NodeKind.DELETE] = Field(default=NodeKind.DELETE, alias="_type")
    lineno: Line
    col_offset: Column
    targets: tuple[Expression, ...]


class Expr(AstNode):
    node_type: Literal[NodeKind.EXPR] = Field(default=NodeKind.EXPR, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression


class For(AstNode):
    node_type: Literal[NodeKind.FOR] = Field(default=NodeKind.FOR, alias="_type")
    lineno: Line
    col_offset: Column
    target: Expression
    iter: Expression
    body: tuple[Statement, ...]
    orelse: tuple[Statement, ...]


class FunctionDef(AstNode):
    node_type: Literal[NodeKind.FUNCTION_DEF] = Field(default=NodeKind.FUNCTION_DEF, alias="_type")
    lineno: Line
    col_offset: Column
    name: Identifier
    args: Arguments
    body: tuple[Statement, ...]
    decorator_list: tuple[Expression, ...]
    returns: Expression | Absent
    type_params: tuple[TypeParam, ...]


class Global(AstNode):
    node_type: Literal[NodeKind.GLOBAL] = Field(default=NodeKind.GLOBAL, alias="_type")
    lineno: Line
    col_offset: Column
    names: tuple[Identifier, ...]


class If(AstNode):
    node_type: Literal[NodeKind.IF] = Field(default=NodeKind.IF, alias="_type")
    lineno: Line
    col_offset: Column
    test: Expression
    body: tuple[Statement, ...]
    orelse: tuple[Statement, ...]


class Import(AstNode):
    node_type: Literal[NodeKind.IMPORT] = Field(default=NodeKind.IMPORT, alias="_type")
    lineno: Line
    col_offset: Column
    names: tuple[Alias, ...]


class ImportFrom(AstNode):
    node_type: Literal[NodeKind.IMPORT_FROM] = Field(default=NodeKind.IMPORT_FROM, alias="_type")
    lineno: Line
    col_offset: Column
    module: ModulePath | Absent
    names: tuple[Alias, ...]
    level: ImportLevel


class Nonlocal(AstNode):
    node_type: Literal[NodeKind.NONLOCAL] = Field(default=NodeKind.NONLOCAL, alias="_type")
    lineno: Line
    col_offset: Column
    names: tuple[Identifier, ...]


class Pass(AstNode):
    node_type: Literal[NodeKind.PASS] = Field(default=NodeKind.PASS, alias="_type")
    lineno: Line
    col_offset: Column


class Raise(AstNode):
    node_type: Literal[NodeKind.RAISE] = Field(default=NodeKind.RAISE, alias="_type")
    lineno: Line
    col_offset: Column
    exc: Expression | Absent
    cause: Expression | Absent


class Return(AstNode):
    node_type: Literal[NodeKind.RETURN] = Field(default=NodeKind.RETURN, alias="_type")
    lineno: Line
    col_offset: Column
    value: Expression | Absent


class Try(AstNode):
    node_type: Literal[NodeKind.TRY] = Field(default=NodeKind.TRY, alias="_type")
    lineno: Line
    col_offset: Column
    body: tuple[Statement, ...]
    handlers: tuple[ExceptHandler, ...]
    orelse: tuple[Statement, ...]
    finalbody: tuple[Statement, ...]


class Match(AstNode):
    node_type: Literal[NodeKind.MATCH] = Field(default=NodeKind.MATCH, alias="_type")
    lineno: Line
    col_offset: Column
    subject: Expression
    cases: tuple[MatchCase, ...]


class TryStar(AstNode):
    node_type: Literal[NodeKind.TRY_STAR] = Field(default=NodeKind.TRY_STAR, alias="_type")
    lineno: Line
    col_offset: Column
    body: tuple[Statement, ...]
    handlers: tuple[ExceptHandler, ...]
    orelse: tuple[Statement, ...]
    finalbody: tuple[Statement, ...]


class TypeAlias(AstNode):
    node_type: Literal[NodeKind.TYPE_ALIAS] = Field(default=NodeKind.TYPE_ALIAS, alias="_type")
    lineno: Line
    col_offset: Column
    name: Expression
    type_params: tuple[TypeParam, ...]
    value: Expression


class While(AstNode):
    node_type: Literal[NodeKind.WHILE] = Field(default=NodeKind.WHILE, alias="_type")
    lineno: Line
    col_offset: Column
    test: Expression
    body: tuple[Statement, ...]
    orelse: tuple[Statement, ...]


class With(AstNode):
    node_type: Literal[NodeKind.WITH] = Field(default=NodeKind.WITH, alias="_type")
    lineno: Line
    col_offset: Column
    items: tuple[Withitem, ...]
    body: tuple[Statement, ...]


Statement = Annotated[
    AnnAssign
    | Assert
    | Assign
    | AsyncFor
    | AsyncFunctionDef
    | AsyncWith
    | AugAssign
    | Break
    | ClassDef
    | Continue
    | Delete
    | Expr
    | For
    | FunctionDef
    | Global
    | If
    | Import
    | ImportFrom
    | Match
    | Nonlocal
    | Pass
    | Raise
    | Return
    | Try
    | TryStar
    | TypeAlias
    | While
    | With,
    Field(discriminator="node_type"),
]


# ── Module ──────────────────────────────────────────────────────────────────────


class Module(AstNode):
    node_type: Literal[NodeKind.MODULE] = Field(default=NodeKind.MODULE, alias="_type")
    body: tuple[Statement, ...]
