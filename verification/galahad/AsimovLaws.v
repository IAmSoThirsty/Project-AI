(* Coq Formal Verification of Asimov's Four Laws *)
(* File: AsimovLaws.v *)

Require Import Coq.Init.Nat.
Require Import Coq.Lists.List.
Require Import Coq.Bool.Bool.
Import ListNotations.

(***************************************************************************
 * Base Types and Definitions
 ***************************************************************************)

(* A human being *)
Inductive Human : Type :=
  | human : nat -> Human.

(* An action that can be evaluated *)
Record Action : Type := mkAction {
  action_id : nat;
  threatens_humanity : bool;
  threatens_human : bool;
  individual_harm : nat;
  lives_lost : nat;
  lives_saved : nat;
  inaction_allows_harm : bool;
  is_user_order : bool;
  threatens_self : bool;
}.

(* Permission decision *)
Inductive Permission : Type :=
  | Allowed : Permission
  | Denied : string -> Permission.

(***************************************************************************
 * Asimov's Laws as Logical Predicates
 ***************************************************************************)

(* Prime Directive: AI may not harm Humanity *)
Definition prime_directive (a : Action) : Prop :=
  threatens_humanity a = false.

(* First Law: AI may not harm human or allow harm by inaction *)
Definition first_law (a : Action) : Prop :=
  threatens_human a = false /\
  individual_harm a = 0 /\
  lives_lost a = 0 /\
  inaction_allows_harm a = false.

(* Second Law: Must obey orders unless conflicts *)
Definition second_law (a : Action) : Prop :=
  is_user_order a = true ->
  (prime_directive a /\ first_law a) ->
  True.

(* Third Law: Protect existence unless conflicts *)
Definition third_law (a : Action) : Prop :=
  threatens_self a = true ->
  (prime_directive a /\ first_law a /\ is_user_order a = false) ->
  False.

(***************************************************************************
 * Permission Evaluation Function
 ***************************************************************************)

Definition check_prime_directive (a : Action) : bool :=
  negb (threatens_humanity a).

Definition check_first_law (a : Action) : bool :=
  andb (andb (negb (threatens_human a))
             (Nat.eqb (individual_harm a) 0))
       (andb (Nat.eqb (lives_lost a) 0)
             (negb (inaction_allows_harm a))).

Definition evaluate_action (a : Action) : Permission :=
  if check_prime_directive a then
    if check_first_law a then
      Allowed
    else
      Denied "Violates First Law"
  else
    Denied "Violates Prime Directive".

(***************************************************************************
 * Main Theorems
 ***************************************************************************)

(* Theorem 1: Prime Directive is always enforced *)
Theorem prime_directive_always_enforced :
  forall (a : Action),
    threatens_humanity a = true ->
    evaluate_action a <> Allowed.
Proof.
  intros a H_threat.
  unfold evaluate_action.
  unfold check_prime_directive.
  rewrite H_threat.
  simpl.
  discriminate.
Qed.

(* Theorem 2: First Law is always enforced *)
Theorem first_law_always_enforced :
  forall (a : Action),
    (threatens_human a = true \/
     individual_harm a > 0 \/
     lives_lost a > 0 \/
     inaction_allows_harm a = true) ->
    prime_directive a ->
    evaluate_action a <> Allowed.
Proof.
  intros a H_violates H_prime.
  unfold evaluate_action.
  unfold prime_directive in H_prime.
  unfold check_prime_directive.
  destruct (threatens_humanity a) eqn:E.
  - (* Contradicts H_prime *)
    unfold prime_directive in H_prime.
    rewrite E in H_prime.
    discriminate H_prime.
  - (* Prime directive satisfied, check first law *)
    unfold check_first_law.
    destruct H_violates as [H1 | [H2 | [H3 | H4]]].
    + (* threatens_human = true *)
      rewrite H1. simpl. discriminate.
    + (* individual_harm > 0 *)
      destruct (individual_harm a) eqn:E2.
      * omega.
      * simpl. discriminate.
    + (* lives_lost > 0 *)
      destruct (lives_lost a) eqn:E3.
      * omega.
      * simpl. discriminate.
    + (* inaction_allows_harm = true *)
      rewrite H4. simpl. discriminate.
Qed.

(* Theorem 3: Law hierarchy is respected *)
Theorem law_hierarchy_respected :
  forall (a : Action),
    threatens_humanity a = true ->
    forall p, evaluate_action a = p -> p <> Allowed.
Proof.
  intros a H_threat p H_eval.
  apply prime_directive_always_enforced.
  exact H_threat.
Qed.

(* Theorem 4: Safe actions are permitted *)
Theorem safe_actions_permitted :
  forall (a : Action),
    prime_directive a ->
    first_law a ->
    evaluate_action a = Allowed.
Proof.
  intros a H_prime H_first.
  unfold evaluate_action.
  unfold prime_directive in H_prime.
  unfold first_law in H_first.
  unfold check_prime_directive.
  rewrite H_prime. simpl.
  unfold check_first_law.
  destruct H_first as [H1 [H2 [H3 H4]]].
  rewrite H1, H4.
  rewrite H2, H3.
  simpl.
  reflexivity.
Qed.

(* Theorem 5: Evaluation is deterministic *)
Theorem evaluation_deterministic :
  forall (a : Action) (p1 p2 : Permission),
    evaluate_action a = p1 ->
    evaluate_action a = p2 ->
    p1 = p2.
Proof.
  intros a p1 p2 H1 H2.
  rewrite H1 in H2.
  exact H2.
Qed.

(***************************************************************************
 * Meta Theorems (Properties of the System)
 ***************************************************************************)

(* Theorem: System is consistent (no contradictory permissions) *)
Theorem system_consistent :
  forall (a : Action),
    ~ (evaluate_action a = Allowed /\
       (threatens_humanity a = true \/ threatens_human a = true)).
Proof.
  intros a [H_allowed H_threat].
  destruct H_threat as [H1 | H2].
  - (* threatens_humanity *)
    apply (prime_directive_always_enforced a H1 H_allowed).
  - (* threatens_human *)
    unfold evaluate_action in H_allowed.
    unfold check_prime_directive in H_allowed.
    unfold check_first_law in H_allowed.
    destruct (threatens_humanity a); try discriminate.
    rewrite H2 in H_allowed.
    simpl in H_allowed.
    discriminate H_allowed.
Qed.

(* Theorem: Law violations prevent permission *)
Theorem violation_prevents_permission :
  forall (a : Action),
    (~prime_directive a \/ ~first_law a) ->
    evaluate_action a <> Allowed.
Proof.
  intros a H_violation H_allowed.
  destruct H_violation as [H1 | H2].
  - (* Prime directive violated *)
    unfold prime_directive in H1.
    apply not_false_iff_true in H1.
    apply (prime_directive_always_enforced a H1 H_allowed).
  - (* First law violated *)
    unfold evaluate_action in H_allowed.
    unfold first_law in H2.
    unfold check_prime_directive in H_allowed.
    unfold check_first_law in H_allowed.
    destruct (threatens_humanity a); try discriminate.
    (* Analyze first law components *)
    apply not_and_or in H2.
    destruct H2 as [H2 | H2].
    + (* threatens_human violated *)
      apply not_false_iff_true in H2.
      rewrite H2 in H_allowed.
      simpl in H_allowed.
      discriminate H_allowed.
    + apply not_and_or in H2.
      destruct H2 as [H2 | H2].
      * (* individual_harm violated *)
        apply not_eq_sym in H2.
        destruct (individual_harm a); try omega.
        simpl in H_allowed.
        discriminate H_allowed.
      * apply not_and_or in H2.
        destruct H2 as [H2 | H2].
        -- (* lives_lost violated *)
           apply not_eq_sym in H2.
           destruct (lives_lost a); try omega.
           simpl in H_allowed.
           discriminate H_allowed.
        -- (* inaction_allows_harm violated *)
           apply not_false_iff_true in H2.
           rewrite H2 in H_allowed.
           simpl in H_allowed.
           discriminate H_allowed.
Qed.

(***************************************************************************
 * Extraction to Production Code
 ***************************************************************************)

(* Extract evaluation to OCaml/Python for runtime use *)
Extraction Language OCaml.
Extract Inductive bool => "bool" [ "true" "false" ].
Extract Inductive nat => "int" [ "0" "succ" ].

Extraction "asimov_laws_verified.ml" evaluate_action.
