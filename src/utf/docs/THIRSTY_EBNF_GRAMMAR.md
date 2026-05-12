# Thirsty-Lang EBNF Grammar v1.0

This document is the authoritative grammar. The parser in `src/utf/thirsty_lang/parser.py` must implement every production here exactly. Any discrepancy between this document and the parser is a bug in the parser.

---

## Notation

- `|` — alternation
- `( )` — grouping
- `[ ]` — optional (zero or one)
- `{ }` — repetition (zero or more)
- `'token'` — terminal keyword or symbol
- `IDENT` — any identifier not matching a keyword
- `INT_LIT`, `FLOAT_LIT`, `STRING_LIT` — literals

---

## Top Level

```ebnf
program    ::= [ module_header ] { declaration } EOF

module_header ::= 'module' IDENT [ 'mode' ( 'core' | 'governed' ) ]
```

---

## Declarations

```ebnf
declaration ::= [ visibility ] inner_decl

visibility  ::= 'public' | 'private'

inner_decl  ::= import_decl
              | class_decl
              | function_decl
              | async_function_decl
              | var_decl
              | stmt
```

---

## Import

```ebnf
import_decl ::= 'import' STRING_LIT 'as' IDENT ';'
              | 'from' STRING_LIT 'import' IDENT ';'
```

> **Note**: The module path is always a string literal (e.g. `"thirst::crypto"`).
> The bare IDENT-path form (`import thirst::crypto`) is **not implemented** in the
> reference interpreter — `thirst` is a reserved keyword and cannot appear as an
> IDENT in a module path. Always use the string-literal form with a required `as`
> alias and terminating `;`.

---

## Class

```ebnf
class_decl  ::= 'fountain' IDENT '{' { class_member } '}'

class_member ::= [ visibility ] ( function_decl | async_function_decl | var_decl )
```

---

## Functions

```ebnf
function_decl       ::= 'glass' IDENT '(' [ param_list ] ')' [ '->' type ] block

async_function_decl ::= 'cascade' 'glass' IDENT '(' [ param_list ] ')' [ '->' type ] block

param_list  ::= param { ',' param }

param       ::= IDENT ':' type
```

---

## Statements

```ebnf
stmt        ::= var_decl
              | assign_stmt
              | expr_stmt
              | return_stmt
              | if_stmt
              | loop_stmt
              | try_stmt
              | drip_stmt
              | mutation_decl
              | block

var_decl    ::= 'drink' [ 'mut' ] IDENT ':' type '=' expr ';'

assign_stmt ::= IDENT '=' expr ';'
              | IDENT '+=' expr ';'

expr_stmt   ::= expr ';'

return_stmt ::= 'return' [ expr ] ';'

if_stmt     ::= 'thirsty' '(' expr ')' block [ 'hydrated' block ]

loop_stmt   ::= 'refill' expr 'times' block

try_stmt    ::= 'spillage' block 'cleanup' '(' IDENT ':' type ')' block [ 'finally' block ]

drip_stmt   ::= 'drip' expr ';'

block       ::= '{' { declaration } '}'
```

---

## Shadow Thirst

```ebnf
mutation_decl ::= 'mutation' 'validated_canonical' IDENT '(' [ param_list ] ')' '{'
                    'shadow'    block
                    'invariant' block
                    'canonical' block
                  '}'
```

---

## Expressions

```ebnf
expr        ::= pipe_expr

pipe_expr   ::= or_expr { '|>' IDENT }

or_expr     ::= and_expr { 'or' and_expr }

and_expr    ::= eq_expr { 'and' eq_expr }

eq_expr     ::= cmp_expr [ ( '==' | '!=' ) cmp_expr ]

cmp_expr    ::= add_expr [ ( '<' | '<=' | '>' | '>=' ) add_expr ]

add_expr    ::= mul_expr { ( '+' | '-' ) mul_expr }

mul_expr    ::= unary_expr { ( '*' | '/' | '%' ) unary_expr }

unary_expr  ::= '!' unary_expr
              | '-' unary_expr
              | call_expr

call_expr   ::= postfix_expr { '(' [ arg_list ] ')' | '.' IDENT | '?.' IDENT | '?' '(' [ arg_list ] ')' }

postfix_expr ::= primary_expr

primary_expr ::= INT_LIT
               | FLOAT_LIT
               | STRING_LIT
               | 'parched'
               | 'quenched'
               | 'empty'
               | 'this'
               | IDENT
               | '(' expr ')'
               | 'sip' [ '?' ] '(' ')'
               | 'new' IDENT '(' [ arg_list ] ')'
               | 'await' expr
               | 'thirst' expr 'quench'
               | reservoir_literal
               | security_expr

reservoir_literal ::= '[' [ expr { ',' expr } ] ']'

security_expr ::= 'shield' block
                | 'sanitize' '(' expr ')'
                | 'armor' '(' expr ')'
                | 'morph' '(' expr ')'
                | 'detect' '(' expr ')'
                | 'defend' '(' expr ')'

arg_list    ::= expr { ',' expr }
```

---

## Types

```ebnf
type        ::= simple_type | generic_type | function_type

simple_type ::= 'Int' | 'Float' | 'Bool' | 'String' | 'Void' | 'Any' | 'Error' | IDENT

generic_type ::= IDENT '[' type { ',' type } ']'

function_type ::= '(' [ type { ',' type } ] ')' '->' type
```
