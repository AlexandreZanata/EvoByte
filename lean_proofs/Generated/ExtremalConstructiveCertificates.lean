-- EvoByte Extremal Constructive Certificates in Finite Additive Combinatorics (P149)
-- Verified mechanically in Lean 4 kernel via `decide` with zero unproven steps.

def pairwise_diffs : List Nat → List Nat
  | [] => []
  | x :: xs => (xs.map (fun y => y - x)) ++ pairwise_diffs xs

def is_sidon_sorted (l : List Nat) : Bool :=
  let diffs := pairwise_diffs l
  diffs.all (fun d => d > 0) && (diffs.eraseDups.length == diffs.length)

theorem sidon_ruzsa_cert_p3 : is_sidon_sorted [4, 5] = true := by decide
theorem sidon_ruzsa_card_p3 : ([4, 5]).length = 2 := by decide
theorem sidon_ruzsa_bound_p3 : [4, 5].all (fun x => x ≤ 5) = true := by decide
theorem sidon_ruzsa_pos_p3 : [4, 5].all (fun x => x > 0) = true := by decide
theorem sidon_ruzsa_cert_p5 : is_sidon_sorted [3, 14, 16, 17] = true := by decide
theorem sidon_ruzsa_card_p5 : ([3, 14, 16, 17]).length = 4 := by decide
theorem sidon_ruzsa_bound_p5 : [3, 14, 16, 17].all (fun x => x ≤ 17) = true := by decide
theorem sidon_ruzsa_pos_p5 : [3, 14, 16, 17].all (fun x => x > 0) = true := by decide
theorem sidon_ruzsa_cert_p7 : is_sidon_sorted [2, 4, 5, 27, 31, 36] = true := by decide
theorem sidon_ruzsa_card_p7 : ([2, 4, 5, 27, 31, 36]).length = 6 := by decide
theorem sidon_ruzsa_bound_p7 : [2, 4, 5, 27, 31, 36].all (fun x => x ≤ 36) = true := by decide
theorem sidon_ruzsa_pos_p7 : [2, 4, 5, 27, 31, 36].all (fun x => x > 0) = true := by decide
theorem sidon_ruzsa_cert_p11 : is_sidon_sorted [7, 39, 58, 63, 65, 86, 92, 100, 101, 104] = true := by decide
theorem sidon_ruzsa_card_p11 : ([7, 39, 58, 63, 65, 86, 92, 100, 101, 104]).length = 10 := by decide
theorem sidon_ruzsa_bound_p11 : [7, 39, 58, 63, 65, 86, 92, 100, 101, 104].all (fun x => x ≤ 104) = true := by decide
theorem sidon_ruzsa_pos_p11 : [7, 39, 58, 63, 65, 86, 92, 100, 101, 104].all (fun x => x > 0) = true := by decide
theorem sidon_ruzsa_cert_p13 : is_sidon_sorted [10, 16, 57, 59, 90, 99, 115, 134, 144, 145, 149, 152] = true := by decide
theorem sidon_ruzsa_card_p13 : ([10, 16, 57, 59, 90, 99, 115, 134, 144, 145, 149, 152]).length = 12 := by decide
theorem sidon_ruzsa_bound_p13 : [10, 16, 57, 59, 90, 99, 115, 134, 144, 145, 149, 152].all (fun x => x ≤ 152) = true := by decide
theorem sidon_ruzsa_pos_p13 : [10, 16, 57, 59, 90, 99, 115, 134, 144, 145, 149, 152].all (fun x => x > 0) = true := by decide
theorem sidon_ruzsa_cert_p17 : is_sidon_sorted [5, 29, 42, 75, 132, 134, 140, 152, 159, 162, 163, 201, 206, 215, 241, 256] = true := by decide
theorem sidon_ruzsa_card_p17 : ([5, 29, 42, 75, 132, 134, 140, 152, 159, 162, 163, 201, 206, 215, 241, 256]).length = 16 := by decide
theorem sidon_ruzsa_bound_p17 : [5, 29, 42, 75, 132, 134, 140, 152, 159, 162, 163, 201, 206, 215, 241, 256].all (fun x => x ≤ 256) = true := by decide
theorem sidon_ruzsa_pos_p17 : [5, 29, 42, 75, 132, 134, 140, 152, 159, 162, 163, 201, 206, 215, 241, 256].all (fun x => x > 0) = true := by decide
theorem sidon_mc_cert_len3 : is_sidon_sorted [1, 2, 4] = true := by decide
theorem sidon_mc_card_len3 : ([1, 2, 4]).length = 3 := by decide
theorem sidon_mc_bound_len3 : [1, 2, 4].all (fun x => x ≤ 4) = true := by decide
theorem sidon_mc_cert_len4 : is_sidon_sorted [1, 2, 4, 8] = true := by decide
theorem sidon_mc_card_len4 : ([1, 2, 4, 8]).length = 4 := by decide
theorem sidon_mc_bound_len4 : [1, 2, 4, 8].all (fun x => x ≤ 8) = true := by decide
theorem sidon_mc_cert_len5 : is_sidon_sorted [1, 2, 4, 8, 13] = true := by decide
theorem sidon_mc_card_len5 : ([1, 2, 4, 8, 13]).length = 5 := by decide
theorem sidon_mc_bound_len5 : [1, 2, 4, 8, 13].all (fun x => x ≤ 13) = true := by decide
theorem sidon_mc_cert_len6 : is_sidon_sorted [1, 2, 4, 8, 13, 21] = true := by decide
theorem sidon_mc_card_len6 : ([1, 2, 4, 8, 13, 21]).length = 6 := by decide
theorem sidon_mc_bound_len6 : [1, 2, 4, 8, 13, 21].all (fun x => x ≤ 21) = true := by decide
theorem sidon_mc_cert_len7 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31] = true := by decide
theorem sidon_mc_card_len7 : ([1, 2, 4, 8, 13, 21, 31]).length = 7 := by decide
theorem sidon_mc_bound_len7 : [1, 2, 4, 8, 13, 21, 31].all (fun x => x ≤ 31) = true := by decide
theorem sidon_mc_cert_len8 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45] = true := by decide
theorem sidon_mc_card_len8 : ([1, 2, 4, 8, 13, 21, 31, 45]).length = 8 := by decide
theorem sidon_mc_bound_len8 : [1, 2, 4, 8, 13, 21, 31, 45].all (fun x => x ≤ 45) = true := by decide
theorem sidon_mc_cert_len9 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66] = true := by decide
theorem sidon_mc_card_len9 : ([1, 2, 4, 8, 13, 21, 31, 45, 66]).length = 9 := by decide
theorem sidon_mc_bound_len9 : [1, 2, 4, 8, 13, 21, 31, 45, 66].all (fun x => x ≤ 66) = true := by decide
theorem sidon_mc_cert_len10 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81] = true := by decide
theorem sidon_mc_card_len10 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81]).length = 10 := by decide
theorem sidon_mc_bound_len10 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81].all (fun x => x ≤ 81) = true := by decide
theorem sidon_mc_cert_len11 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97] = true := by decide
theorem sidon_mc_card_len11 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97]).length = 11 := by decide
theorem sidon_mc_bound_len11 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97].all (fun x => x ≤ 97) = true := by decide
theorem sidon_mc_cert_len12 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123] = true := by decide
theorem sidon_mc_card_len12 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123]).length = 12 := by decide
theorem sidon_mc_bound_len12 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123].all (fun x => x ≤ 123) = true := by decide
theorem sidon_mc_cert_len13 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148] = true := by decide
theorem sidon_mc_card_len13 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148]).length = 13 := by decide
theorem sidon_mc_bound_len13 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148].all (fun x => x ≤ 148) = true := by decide
theorem sidon_mc_cert_len14 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182] = true := by decide
theorem sidon_mc_card_len14 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182]).length = 14 := by decide
theorem sidon_mc_bound_len14 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182].all (fun x => x ≤ 182) = true := by decide
theorem sidon_mc_cert_len15 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182, 204] = true := by decide
theorem sidon_mc_card_len15 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182, 204]).length = 15 := by decide
theorem sidon_mc_bound_len15 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182, 204].all (fun x => x ≤ 204) = true := by decide
theorem sidon_mc_cert_len16 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182, 204, 252] = true := by decide
theorem sidon_mc_card_len16 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182, 204, 252]).length = 16 := by decide
theorem sidon_mc_bound_len16 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182, 204, 252].all (fun x => x ≤ 252) = true := by decide
theorem sidon_singer_cert_q2 : is_sidon_sorted [1, 2, 4] = true := by decide
theorem sidon_singer_card_q2 : ([1, 2, 4]).length = 3 := by decide
theorem sidon_singer_bound_q2 : [1, 2, 4].all (fun x => x ≤ 4) = true := by decide
theorem sidon_singer_cert_q3 : is_sidon_sorted [1, 2, 4, 10] = true := by decide
theorem sidon_singer_card_q3 : ([1, 2, 4, 10]).length = 4 := by decide
theorem sidon_singer_bound_q3 : [1, 2, 4, 10].all (fun x => x ≤ 10) = true := by decide
theorem sidon_singer_cert_q4 : is_sidon_sorted [1, 2, 5, 15, 17] = true := by decide
theorem sidon_singer_card_q4 : ([1, 2, 5, 15, 17]).length = 5 := by decide
theorem sidon_singer_bound_q4 : [1, 2, 5, 15, 17].all (fun x => x ≤ 17) = true := by decide
theorem sidon_singer_cert_q5 : is_sidon_sorted [1, 2, 4, 9, 13, 19] = true := by decide
theorem sidon_singer_card_q5 : ([1, 2, 4, 9, 13, 19]).length = 6 := by decide
theorem sidon_singer_bound_q5 : [1, 2, 4, 9, 13, 19].all (fun x => x ≤ 19) = true := by decide
theorem sidon_bnb_cert_n10 : is_sidon_sorted [1, 2, 4, 8] = true := by decide
theorem sidon_bnb_card_n10 : ([1, 2, 4, 8]).length = 4 := by decide
theorem sidon_bnb_bound_n10 : [1, 2, 4, 8].all (fun x => x ≤ 8) = true := by decide
theorem sidon_bnb_cert_n20 : is_sidon_sorted [1, 2, 4, 8, 13] = true := by decide
theorem sidon_bnb_card_n20 : ([1, 2, 4, 8, 13]).length = 5 := by decide
theorem sidon_bnb_bound_n20 : [1, 2, 4, 8, 13].all (fun x => x ≤ 13) = true := by decide
theorem sidon_bnb_cert_n30 : is_sidon_sorted [1, 2, 4, 8, 13, 21] = true := by decide
theorem sidon_bnb_card_n30 : ([1, 2, 4, 8, 13, 21]).length = 6 := by decide
theorem sidon_bnb_bound_n30 : [1, 2, 4, 8, 13, 21].all (fun x => x ≤ 21) = true := by decide
theorem sidon_bnb_cert_n40 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31] = true := by decide
theorem sidon_bnb_card_n40 : ([1, 2, 4, 8, 13, 21, 31]).length = 7 := by decide
theorem sidon_bnb_bound_n40 : [1, 2, 4, 8, 13, 21, 31].all (fun x => x ≤ 31) = true := by decide
theorem sidon_bnb_cert_n50 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45] = true := by decide
theorem sidon_bnb_card_n50 : ([1, 2, 4, 8, 13, 21, 31, 45]).length = 8 := by decide
theorem sidon_bnb_bound_n50 : [1, 2, 4, 8, 13, 21, 31, 45].all (fun x => x ≤ 45) = true := by decide
theorem sidon_bnb_cert_n60 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45] = true := by decide
theorem sidon_bnb_card_n60 : ([1, 2, 4, 8, 13, 21, 31, 45]).length = 8 := by decide
theorem sidon_bnb_bound_n60 : [1, 2, 4, 8, 13, 21, 31, 45].all (fun x => x ≤ 45) = true := by decide
theorem sidon_bnb_cert_n75 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66] = true := by decide
theorem sidon_bnb_card_n75 : ([1, 2, 4, 8, 13, 21, 31, 45, 66]).length = 9 := by decide
theorem sidon_bnb_bound_n75 : [1, 2, 4, 8, 13, 21, 31, 45, 66].all (fun x => x ≤ 66) = true := by decide
theorem sidon_bnb_cert_n100 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97] = true := by decide
theorem sidon_bnb_card_n100 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97]).length = 11 := by decide
theorem sidon_bnb_bound_n100 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97].all (fun x => x ≤ 97) = true := by decide
theorem sidon_bnb_cert_n120 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97] = true := by decide
theorem sidon_bnb_card_n120 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97]).length = 11 := by decide
theorem sidon_bnb_bound_n120 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97].all (fun x => x ≤ 97) = true := by decide
theorem sidon_bnb_cert_n150 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148] = true := by decide
theorem sidon_bnb_card_n150 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148]).length = 13 := by decide
theorem sidon_bnb_bound_n150 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148].all (fun x => x ≤ 148) = true := by decide
theorem sidon_bnb_cert_n180 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148] = true := by decide
theorem sidon_bnb_card_n180 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148]).length = 13 := by decide
theorem sidon_bnb_bound_n180 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148].all (fun x => x ≤ 148) = true := by decide
theorem sidon_bnb_cert_n200 : is_sidon_sorted [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182] = true := by decide
theorem sidon_bnb_card_n200 : ([1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182]).length = 14 := by decide
theorem sidon_bnb_bound_n200 : [1, 2, 4, 8, 13, 21, 31, 45, 66, 81, 97, 123, 148, 182].all (fun x => x ≤ 182) = true := by decide