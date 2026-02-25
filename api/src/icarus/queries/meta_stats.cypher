CALL {
  MATCH (n) RETURN count(n) AS total_nodes
}
CALL {
  MATCH ()-[r]->() RETURN count(r) AS total_relationships
}
CALL {
  MATCH (p:Person) RETURN count(p) AS person_count
}
CALL {
  MATCH (c:Company) RETURN count(c) AS company_count
}
CALL {
  MATCH (h:Health) RETURN count(h) AS health_count
}
CALL {
  MATCH (f:Finance) RETURN count(f) AS finance_count
}
CALL {
  MATCH (c:Contract) RETURN count(c) AS contract_count
}
CALL {
  MATCH (s:Sanction) RETURN count(s) AS sanction_count
}
CALL {
  MATCH (e:Election) RETURN count(e) AS election_count
}
CALL {
  MATCH (a:Amendment) RETURN count(a) AS amendment_count
}
CALL {
  MATCH (e:Embargo) RETURN count(e) AS embargo_count
}
CALL {
  MATCH (e:Education) RETURN count(e) AS education_count
}
CALL {
  MATCH (c:Convenio) RETURN count(c) AS convenio_count
}
CALL {
  MATCH (l:LaborStats) RETURN count(l) AS laborstats_count
}
CALL {
  MATCH (o:OffshoreEntity) RETURN count(o) AS offshore_entity_count
}
CALL {
  MATCH (o:OffshoreOfficer) RETURN count(o) AS offshore_officer_count
}
CALL {
  MATCH (g:GlobalPEP) RETURN count(g) AS global_pep_count
}
CALL {
  MATCH (c:CVMProceeding) RETURN count(c) AS cvm_proceeding_count
}
CALL {
  MATCH (e:Expense) RETURN count(e) AS expense_count
}
CALL {
  MATCH (p:PEPRecord) RETURN count(p) AS pep_record_count
}
CALL {
  MATCH (e:Expulsion) RETURN count(e) AS expulsion_count
}
CALL {
  MATCH (l:LeniencyAgreement) RETURN count(l) AS leniency_count
}
CALL {
  MATCH (s:InternationalSanction) RETURN count(s) AS international_sanction_count
}
CALL {
  MATCH (g:GovCardExpense) RETURN count(g) AS gov_card_expense_count
}
CALL {
  MATCH (t:GovTravel) RETURN count(t) AS gov_travel_count
}
CALL {
  MATCH (b:Bid) RETURN count(b) AS bid_count
}
CALL {
  MATCH (f:Fund) RETURN count(f) AS fund_count
}
CALL {
  MATCH (d:DOUAct) RETURN count(d) AS dou_act_count
}
CALL {
  MATCH (t:TaxWaiver) RETURN count(t) AS tax_waiver_count
}
CALL {
  MATCH (m:MunicipalFinance) RETURN count(m) AS municipal_finance_count
}
CALL {
  MATCH (d:DeclaredAsset) RETURN count(d) AS declared_asset_count
}
CALL {
  MATCH (pm:PartyMembership) RETURN count(pm) AS party_membership_count
}
CALL {
  MATCH (b:BarredNGO) RETURN count(b) AS barred_ngo_count
}
CALL {
  MATCH (b:BCBPenalty) RETURN count(b) AS bcb_penalty_count
}
CALL {
  MATCH (lm:LaborMovement) RETURN count(lm) AS labor_movement_count
}
CALL {
  MATCH (lc:LegalCase) RETURN count(lc) AS legal_case_count
}
CALL {
  MATCH (c:CPI) RETURN count(c) AS cpi_count
}
RETURN total_nodes, total_relationships,
       person_count, company_count, health_count,
       finance_count, contract_count, sanction_count,
       election_count, amendment_count, embargo_count,
       education_count, convenio_count, laborstats_count,
       offshore_entity_count, offshore_officer_count,
       global_pep_count, cvm_proceeding_count, expense_count,
       pep_record_count, expulsion_count, leniency_count,
       international_sanction_count,
       gov_card_expense_count, gov_travel_count, bid_count,
       fund_count, dou_act_count, tax_waiver_count,
       municipal_finance_count,
       declared_asset_count, party_membership_count,
       barred_ngo_count, bcb_penalty_count,
       labor_movement_count, legal_case_count, cpi_count
