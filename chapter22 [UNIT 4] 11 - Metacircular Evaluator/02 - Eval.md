## eval

    
    (define (eval-1 exp)
      (cond ((constant? exp) exp)
            ((symbol? exp) (eval exp))      ; use underlying Scheme's EVAL                        
            ((quote-exp? exp) (cadr exp))
            ((if-exp? exp)
             (if (eval-1 (cadr exp))
                 (eval-1 (caddr exp))
                 (eval-1 (cadddr exp))))
            ((lambda-exp? exp) exp)
            ((pair? exp) (apply-1 (eval-1 (car exp))      ; eval the operator                     
                                  (map eval-1 (cdr exp))))
            (else (error "bad expr: " exp))))
    

Does this code look familar to you? It should, it's part of the Scheme-1
interpreter you learned in Lesson 6! If you look at line 3, you can see that
`eval-1` is using Scheme's `eval` procedure. You didn't really have to worry
too much about the details in Lesson 6, because Scheme's `eval` procedure
handled all the details. But then how is `eval` defined?

Now is time to look at how `eval` is written. Take a look, and compare it to
`eval-1`:

    
    (define (eval exp env)
      (cond ((self-evaluating? exp) exp)
            ((variable? exp) (lookup-variable-value exp env))
            ((quoted? exp) (text-of-quotation exp))
            ((assignment? exp) (eval-assignment exp env))
            ((definition? exp) (eval-definition exp env))
            ((if? exp) (eval-if exp env))
            ((lambda? exp)
             (make-procedure (lambda-parameters exp)
                             (lambda-body exp)
                             env))
            ((begin? exp) 
             (eval-sequence (begin-actions exp) env))
            ((cond? exp) (eval (cond->if exp) env))
            ((application? exp)
             (apply (eval (operator exp) env)
                    (list-of-values (operands exp) env)))
            (else
             (error "Unknown expression type -- EVAL" exp))))
    

Don't worry if you don't understand it. We will go through this code step-by-
step.

## what does eval do?

`Eval` takes as arguments an expression and an environment. It classifies the
expression and directs its evaluation. Eval is structured as a case analysis
of the syntactic type of the expression to be evaluated. In order to keep the
procedure general, we express the determination of the type of an expression
abstractly, making no commitment to any particular representation for the
various types of expressions. Each type of expression has a predicate that
tests for it and an abstract means for selecting its parts.

When `eval` processes a procedure application, it uses `list-of-values` to
produce the list of arguments to which the procedure is to be applied. `List-
of-values` takes as an argument the operands of the combination. It evaluates
each operand and returns a list of the corresponding values:

    
    (define (list-of-values exps env)
      (if (no-operands? exps)
          '()
          (cons (eval (first-operand exps) env)
                (list-of-values (rest-operands exps) env))))
    

## PRIMITIVE EXPRESSIONS

![](http://www.bbc.co.uk/music/tinthepark/2010/img/home/radio1_small_promo.jpg
)

For self-evaluating expressions, such as numbers, `eval` returns the
expression itself. `Eval` must look up variables in the environment to find
their values.

  * The only self-evaluating items are numbers and strings:
    
    (define (self-evaluating? exp)
      (cond ((number? exp) true)
            ((string? exp) true)
            (else false)))
    

Remember, words are **not** strings. Strings use double quotes (e.g. `"Hello,
world!"`).

  * Variables are represented by symbols:
    
    
    (define (variable? exp)
      (symbol? exp))

## Special Forms

![](https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcQzrLHmk190OIaf1
-xqLtrpW-BYa-yWwYHL58ZZBqQw6AVbqSZ2qw)

  * For quoted expressions, `eval` returns the expression that was quoted.

Quotations have the form `(quote <text-of-quotation>)`:

    
    
    (define (quoted? exp)
      (tagged-list? exp 'quote))
    
    (define (text-of-quotation exp) (cadr exp))
    

`Quoted?` is defined in terms of the procedure `tagged-list?`, which
identifies lists beginning with a designated symbol:

    
    
    (define (tagged-list? exp tag)
      (if (pair? exp)
          (eq? (car exp) tag)
          false))
    

  * A `lambda` expression must be transformed into an applicable procedure by packaging together the parameters and body specified by the lambda expression with the environment of the evaluation.

Lambda expressions are lists that begin with the symbol lambda:

    
    
    (define (lambda? exp) (tagged-list? exp 'lambda))
    (define (lambda-parameters exp) (cadr exp))
    (define (lambda-body exp) (cddr exp))
    

There is a constructor for lambda expressions, which is used by `definition-
value`:

    
    
    (define (make-lambda parameters body)
      (cons 'lambda (cons parameters body)))
    

## special forms: sequences

![](http://x-equals.com/blog/wp-content/editing_sequences_5_seq_1280.jpg)

  * `Eval-sequence` is used by `apply` to evaluate the sequence of expressions in a procedure body. It is also used by `eval` to evaluate the sequence of expressions in a `begin` expression. It takes as arguments a sequence of expressions and an environment, and evaluates the expressions in the order in which they occur. The value returned is the value of the final expression.
    
    (define (eval-sequence exps env)
      (cond ((last-exp? exps) (eval (first-exp exps) env))
            (else (eval (first-exp exps) env)
                  (eval-sequence (rest-exps exps) env))))
    

  * `Begin` packages a sequence of expressions into a single expression. A `begin` expression requires evaluating its sequence of expressions in the order in which they appear. We include syntax operations on `begin` expressions to extract the actual sequence from the `begin` expression, as well as selectors that return the first expression and the rest of the expressions in the sequence.
    
    (define (begin? exp) (tagged-list? exp 'begin))
    (define (begin-actions exp) (cdr exp))
    (define (last-exp? seq) (null? (cdr seq)))
    (define (first-exp seq) (car seq))
    (define (rest-exps seq) (cdr seq))
    

There is a constructor `sequence->exp` (for use by `cond->if`) that transforms
a sequence into a single expression, using `begin` if necessary:

    
    (define (sequence->exp seq)
      (cond ((null? seq) seq)
            ((last-exp? seq) (first-exp seq))
            (else (make-begin seq))))
    (define (make-begin seq) (cons 'begin seq))

## Special Forms: Conditionals

![](http://callofcarly.files.wordpress.com/2011/10/if.png)

  * `Eval-if` evaluates the predicate part of an if expression in the given environment. If the result is true, eval-if evaluates the consequent, otherwise it evaluates the alternative: 
    
    (define (eval-if exp env)
      (if (true? (eval (if-predicate exp) env))
          (eval (if-consequent exp) env)
          (eval (if-alternative exp) env)))
    

The use of `true?` in `eval-if` highlights the issue of the connection between
an implemented language and an implementation language. The `if-predicate` is
evaluated in the language being implemented and thus yields a value in that
language. The interpreter predicate `true?` translates that value into a value
that can be tested by the if in the implementation language: The metacircular
representation of truth might not be the same as that of the underlying
Scheme.

`true?` and `false?` are define as following:

    
    (define (true? x)
      (not (eq? x false)))
    (define (false? x)
      (eq? x false))
    

  * An `if` expression requires special processing of its parts, so as to evaluate the consequent if the predicate is true, and otherwise to evaluate the alternative.
    
    (define (if? exp) (tagged-list? exp 'if))
    (define (if-predicate exp) (cadr exp))
    (define (if-consequent exp) (caddr exp))
    (define (if-alternative exp)
      (if (not (null? (cdddr exp)))
          (cadddr exp)
          'false))
    

There is a constructor for `if` expressions, to be used by `cond->if` to
transform cond expressions into `if` expressions:

    
    (define (make-if predicate consequent alternative)
      (list 'if predicate consequent alternative))
    

  * A case analysis (`cond`) is transformed into a nest of `if` expressions and then evaluated.

For example,

    
    (cond ((> x 0) x)
          ((= x 0) (display 'zero) 0)
          (else (- x)))
    

can be represented as:

    
    (if (> x 0)
        x
        (if (= x 0)
            (begin (display 'zero)
                   0)
            (- x)))
    

There are syntax procedures that extract the parts of a cond expression, and a
procedure `cond->if` that transforms `cond` expressions into `if` expressions.
A case analysis begins with `cond` and has a list of predicate-action clauses.
A clause is an `else` clause if its predicate is the symbol `else`.

    
    (define (cond? exp) (tagged-list? exp 'cond))
    (define (cond-clauses exp) (cdr exp))
    (define (cond-else-clause? clause)
      (eq? (cond-predicate clause) 'else))
    (define (cond-predicate clause) (car clause))
    (define (cond-actions clause) (cdr clause))
    (define (cond->if exp)
      (expand-clauses (cond-clauses exp)))
    
    (define (expand-clauses clauses)
      (if (null? clauses)
          'false                          ; no else clause
          (let ((first (car clauses))
                (rest (cdr clauses)))
            (if (cond-else-clause? first)
                (if (null? rest)
                    (sequence->exp (cond-actions first))
                    (error "ELSE clause isn't last -- COND->IF"
                           clauses))
                (make-if (cond-predicate first)
                         (sequence->exp (cond-actions first))
                         (expand-clauses rest))))))
    

Expressions (such as `cond`) that we choose to implement as syntactic
transformations are called **derived expressions**. `Let` expressions are also
derived expressions.

## Special forms: assignments and definitions

![](http://2.bp.blogspot.com/-BJ9VKWsOh74/UjWTv9D1TZI/AAAAAAAAfFA/c0x9oTVm2S4/
s1600/DEFINE_TwitterAvatar_R1_eo.png)

An assignment to (or a definition of) a variable must recursively call `eval`
to compute the new value to be associated with the variable. The environment
must be modified to change (or create) the binding of the variable.

The following procedure handles assignments to variables. It calls `eval` to
find the value to be assigned and transmits the variable and the resulting
value to `set-variable-value!` to be installed in the designated environment.

    
    (define (eval-assignment exp env)
      (set-variable-value! (assignment-variable exp)
                           (eval (assignment-value exp) env)
                           env)
      'ok)
    

Definitions of variables are handled in a similar manner:

    
    (define (eval-definition exp env)
      (define-variable! (definition-variable exp)
                        (eval (definition-value exp) env)
                        env)
      'ok)
    

By convention, the symbol `ok` is returned as the value of an assignment or a
definition.

Now let's look at how assignment expressions are represented.

Assignments have the form `(set! <var> <value>)`:

    
    (define (assignment? exp)
      (tagged-list? exp 'set!))
    (define (assignment-variable exp) (cadr exp))
    (define (assignment-value exp) (caddr exp))

Definitions have the form `(define <var> <value>)` or the form

    
    (define (var parameter1 ... parametern)
      body)
    

The latter form (standard procedure definition) can be re-written as:

    
    (define var
      (lambda (parameter1 ... parametern)
              body))
    

The corresponding syntax procedures are the following:

    
    (define (definition? exp)
      (tagged-list? exp 'define))
    (define (definition-variable exp)
      (if (symbol? (cadr exp))
          (cadr exp)
          (caadr exp)))
    (define (definition-value exp)
      (if (symbol? (cadr exp))
          (caddr exp)
          (make-lambda (cdadr exp)   ; formal parameters
                       (cddr exp)))) ; body

## eval definition revisited

Let's take a look at `eval`'s definition again. Does it make sense to you now?

    
    (define (eval exp env)
      (cond ((self-evaluating? exp) exp)
            ((variable? exp) (lookup-variable-value exp env))
            ((quoted? exp) (text-of-quotation exp))
            ((assignment? exp) (eval-assignment exp env))
            ((definition? exp) (eval-definition exp env))
            ((if? exp) (eval-if exp env))
            ((lambda? exp)
             (make-procedure (lambda-parameters exp)
                             (lambda-body exp)
                             env))
            ((begin? exp) 
             (eval-sequence (begin-actions exp) env))
            ((cond? exp) (eval (cond->if exp) env))
            ((application? exp)
             (apply (eval (operator exp) env)
                    (list-of-values (operands exp) env)))
            (else
             (error "Unknown expression type -- EVAL" exp))))  
    

_Wait, wait, what's apply? I don't know what that is!_

We are going to explore it in the next subsection.

## takeaways

In this subsection, you learned how Scheme evaluates the expressions using
`eval` and other procedures.

## What's next?

Go to the next subsection and learn how Scheme applies the evaluated
expressions!
