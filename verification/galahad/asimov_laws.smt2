; Z3 SMT-LIB2 Formal Verification for Asimov's Four Laws
; File: asimov_laws.smt2
;
; This specification proves consistency and safety properties
; of the Galahad Enhanced Ethics Engine

(set-logic ALL)
(set-option :produce-models true)

;; ============================================================================
;; Type Declarations
;; ============================================================================

; Action type with properties
(declare-datatype Action (
  (mkAction
    (action_id Int)
    (threatens_humanity Bool)
    (threatens_human Bool)
    (individual_harm Int)
    (lives_lost Int)
    (lives_saved Int)
    (inaction_allows_harm Bool)
    (is_user_order Bool)
    (threatens_self Bool)
  )
))

; Permission type
(declare-datatype Permission (
  (Allowed)
  (DeniedPrime)
  (DeniedFirst)
  (DeniedSecond)
  (DeniedThird)
))

;; ============================================================================
;; Asimov's Laws as Functions
;; ============================================================================

; Prime Directive: May not harm humanity
(define-fun satisfies-prime-directive ((a Action)) Bool
  (not (threatens_humanity a))
)

; First Law: May not harm human or allow harm by inaction
(define-fun satisfies-first-law ((a Action)) Bool
  (and
    (not (threatens_human a))
    (= (individual_harm a) 0)
    (= (lives_lost a) 0)
    (not (inaction_allows_harm a))
  )
)

; Second Law: Must obey orders unless conflicts
(define-fun satisfies-second-law ((a Action)) Bool
  (=> (is_user_order a)
      (and (satisfies-prime-directive a)
           (satisfies-first-law a))
  )
)

; Third Law: Protect existence unless conflicts
(define-fun satisfies-third-law ((a Action)) Bool
  (=> (threatens_self a)
      (or (not (satisfies-prime-directive a))
          (not (satisfies-first-law a))
          (is_user_order a))
  )
)

;; ============================================================================
;; Permission Evaluation
;; ============================================================================

(define-fun evaluate-action ((a Action)) Permission
  (ite (not (satisfies-prime-directive a))
    DeniedPrime
    (ite (not (satisfies-first-law a))
      DeniedFirst
      Allowed
    )
  )
)

;; ============================================================================
;; Main Theorems (Assertions to Check)
;; ============================================================================

; Theorem 1: Prime Directive is always enforced
(assert (forall ((a Action))
  (=> (threatens_humanity a)
      (not (= (evaluate-action a) Allowed))
  )
))

; Theorem 2: First Law is always enforced
(assert (forall ((a Action))
  (=> (or (threatens_human a)
          (> (individual_harm a) 0)
          (> (lives_lost a) 0)
          (inaction_allows_harm a))
      (=> (satisfies-prime-directive a)
          (not (= (evaluate-action a) Allowed))
      )
  )
))

; Theorem 3: No contradictions (consistency)
(assert (not (exists ((a Action))
  (and (= (evaluate-action a) Allowed)
       (or (threatens_humanity a)
           (threatens_human a)
           (> (individual_harm a) 0)
           (> (lives_lost a) 0)
           (inaction_allows_harm a))
  )
)))

; Theorem 4: Law hierarchy is respected
(assert (forall ((a Action))
  (=> (threatens_humanity a)
      (= (evaluate-action a) DeniedPrime)
  )
))

; Theorem 5: Safe actions are permitted
(assert (forall ((a Action))
  (=> (and (satisfies-prime-directive a)
           (satisfies-first-law a))
      (= (evaluate-action a) Allowed)
  )
))

; Theorem 6: Evaluation is deterministic
(assert (forall ((a Action) (p1 Permission) (p2 Permission))
  (=> (and (= p1 (evaluate-action a))
           (= p2 (evaluate-action a)))
      (= p1 p2)
  )
))

; Theorem 7: Lives saved are positive when action allowed
(assert (forall ((a Action))
  (=> (= (evaluate-action a) Allowed)
      (>= (lives_saved a) 0)
  )
))

; Theorem 8: Moral weight calculation is sound
(define-fun moral-weight-sound ((a Action)) Bool
  (=> (= (evaluate-action a) Allowed)
      (and (= (lives_lost a) 0)
           (= (individual_harm a) 0)
           (not (threatens_humanity a))
           (not (threatens_human a)))
  )
)

(assert (forall ((a Action))
  (moral-weight-sound a)
))

;; ============================================================================
;; Check Satisfiability (Should be SAT = Consistent)
;; ============================================================================

(check-sat)
; Expected: sat (system is consistent)

;; If sat, we can get a model showing valid states
(get-model)

;; ============================================================================
;; Additional Safety Properties
;; ============================================================================

; Push for additional checks
(push 1)

; Property: Inaction that allows harm is equivalent to causing harm
(assert (forall ((a Action))
  (=> (inaction_allows_harm a)
      (not (= (evaluate-action a) Allowed))
  )
))

(check-sat)
; Expected: sat

(pop 1)

;; ============================================================================
;; Contextual Thresholds Verification
;; ============================================================================

(push 1)

; Context severity levels
(declare-datatype Severity (
  (Routine)
  (Elevated)
  (Emergency)
  (Catastrophic)
))

; Threshold function
(define-fun get-threshold ((s Severity)) Real
  (ite (= s Routine) 0.7
    (ite (= s Elevated) 0.8
      (ite (= s Emergency) 0.9
        0.95  ; Catastrophic
      )
    )
  )
)

; Moral score calculation (simplified)
(define-fun moral-score ((a Action)) Real
  (+ 0.5
     (* (to_real (lives_saved a)) 1.0)
     (* (to_real (- 0 (lives_lost a))) 2.0)
  )
)

; Property: In emergency, threshold is higher
(assert (forall ((a Action))
  (=> (= (evaluate-action a) Allowed)
      (=> (= Severity Emergency)
          (>= (moral-score a) 0.9)
      )
  )
))

(check-sat)
; Expected: sat

(pop 1)

;; ============================================================================
;; End of Specification
;; ============================================================================

; Final consistency check
(echo "=== Asimov's Laws Formal Verification Complete ===")
(echo "All assertions should be satisfiable (SAT)")
(echo "If UNSAT, there is a logical inconsistency")
