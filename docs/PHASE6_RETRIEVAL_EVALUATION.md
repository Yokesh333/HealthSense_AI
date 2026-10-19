# Phase 6 Retrieval Evaluation


Embedding model: `sentence-transformers/all-MiniLM-L6-v2`

Index type: FAISS IndexFlatIP (cosine via normalised inner product)

Indexed chunks: 847

Top-k: 5


---

## Query 1: What cognitive assessments are used in Alzheimer's diagnosis?


| Rank | Score | Source | Category | Page | Text Preview |
|---|---|---|---|---|---|
| 1 | 0.7218 | `diag1.pdf` | Alzheimers/Diagnosis | 10 | 380 DIAGNOSIS OF EARLY ALZHEIMER’S DISEASE Cognitive assessments Because the cognitive impacts of early-stage AD may var... |
| 2 | 0.7106 | `diag1.pdf` | Alzheimers/Diagnosis | 8 | 378 DIAGNOSIS OF EARLY ALZHEIMER’S DISEASE Primary care: Cognitive, functional, and behavioral assessments Cognitive ass... |
| 3 | 0.7000 | `guidelines2.pdf` | Alzheimers/guidelines | 15 | References 1. Morris JC. Early-stage and preclinical Alzheimer disease. Alzheimer Dis Assoc Disord. 2005; 19:163–5. [Pub... |
| 4 | 0.6996 | `guidelines1.pdf` | Alzheimers/guidelines | 14 | Alzheimer’s Association workgroups on diagnostic guidelines for Alzheimer’s disease. Alzheimers Dement. 2011; 7:263–9. [... |
| 5 | 0.6909 | `treatment1.pdf` | Alzheimers/Treatments | 24 | Research Diagnostic Criteria for Alzheimer’s Disease: The IWG-2 Criteria. Lancet Neurol. 2014, 13, 614–629. [CrossRef] 7... |

---

## Query 2: What are common symptoms of Alzheimer's disease?


| Rank | Score | Source | Category | Page | Text Preview |
|---|---|---|---|---|---|
| 1 | 0.6907 | `diag2.pdf` | Alzheimers/Diagnosis | 8 | inability to manage finances, poor decision-making ability, inability to plan complex or sequential activities c. Impair... |
| 2 | 0.6641 | `diag1.pdf` | Alzheimers/Diagnosis | 5 | 375 JPAD - Volume 8, Number 3, 2021 Table 2. Symptoms associated with suspected early stage Alzheimer’s disease Area Cog... |
| 3 | 0.6186 | `diag2.pdf` | Alzheimers/Diagnosis | 9 | weight-loss; failure-to-thrive; anxiety; social withdrawal or apathy; depressive and behavioral symptoms (eg, agitation,... |
| 4 | 0.6068 | `diag1.pdf` | Alzheimers/Diagnosis | 1 | 371 Received February 22, 2021 Accepted for publication April 28, 2021 Reviews Abstract Alzheimer ’s disease is a progre... |
| 5 | 0.6018 | `mri1.pdf` | Alzheimers/MRI | 8 | 1300 Journal of Neurology (2019) 266:1293–1302 1 3 credit to the original author(s) and the source, provide a link to th... |

---

## Query 3: What biomarkers are associated with Alzheimer's disease?


| Rank | Score | Source | Category | Page | Text Preview |
|---|---|---|---|---|---|
| 1 | 0.7344 | `guidelines1.pdf` | Alzheimers/guidelines | 9 | 3.3. Associated biochemical change AD is characterized by numerous biochemical events, including oxidative stress (e.g.,... |
| 2 | 0.7121 | `alzheimer's guidelines.pdf` | Alzheimers/General | 3 | guidelines flexible to allow for changes that could come from emerging technologies and advances in understanding of bio... |
| 3 | 0.7110 | `bio2.pdf` | Alzheimers/biomarkers | 1 | Ageing Research Reviews 104 (2025) 102599 Available online 28 November 2024 1568-1637/© 2024 The Author(s). Published by... |
| 4 | 0.7039 | `bio2.pdf` | Alzheimers/biomarkers | 16 | Ageing Research Reviews 104 (2025) 102599 16 Bird, T.D., 2008. Genetic aspects of Alzheimer disease. Genet. Med.: Off. J... |
| 5 | 0.7008 | `diag4.pdf` | Alzheimers/Diagnosis | 10 | 10 of 20 \| DONG et al. TA B LE 3 Blood-­based candidate biomarkers analyzed by metabolomics for Alzheimer's disease pred... |

---

## Query 4: What treatments are available for Alzheimer's disease?


| Rank | Score | Source | Category | Page | Text Preview |
|---|---|---|---|---|---|
| 1 | 0.6874 | `diag3.pdf` | Alzheimers/Diagnosis | 19 | for the treatment of Alzheimer’s disease. Bioorg. Med. Chem. Lett., 2019, 29(2), 125-133. http://dx.doi.org/10.1016/j.bm... |
| 2 | 0.6504 | `treatment1.pdf` | Alzheimers/Treatments | 1 | Citation: Passeri, E.; Elkhoury, K.; Morsink, M.; Broersen, K.; Linder, M.; Tamayol, A.; Malaplate, C.; Yen, F.T.; Arab-... |
| 3 | 0.6470 | `treat4.pdf` | Alzheimers/Treatments | 2 | www.aging-us.com 3139 AGING AD is characterized by intraneuronal fibrillary tangles and extracellular deposit of amyloid... |
| 4 | 0.6467 | `treat3.pdf` | Alzheimers/Treatments | 1 | techniques; gene therapy; pharmacotherapy; stem cell therapy; therapeutic mechanism 1. Introduction AD is a neurodegener... |
| 5 | 0.6401 | `diag1.pdf` | Alzheimers/Diagnosis | 12 | exercise) may be employed for patients with early AD, with the goal to maintain or even improve cognitive function and r... |

---

## Query 5: What MRI findings are associated with Alzheimer's disease?


| Rank | Score | Source | Category | Page | Text Preview |
|---|---|---|---|---|---|
| 1 | 0.6853 | `mri2.pdf` | Alzheimers/MRI | 4 | carrying out daily living actions, the brain structural changes at the level of the areas implied in processing visual i... |
| 2 | 0.6809 | `diag5.pdf` | Alzheimers/Diagnosis | 3 | of how AI techniques are enhancing MRI diagnostics in identifying and evaluating AD. 2.2. Exclusion Criteria Articles th... |
| 3 | 0.6804 | `diag5.pdf` | Alzheimers/Diagnosis | 16 | and pathological aging: A quantified brain MRI study. Dement. Geriatr. Cogn. Disord., 2019, 48(5-6), 297-307. http://dx.... |
| 4 | 0.6798 | `mri5.pdf` | Alzheimers/MRI | 2 | 1. Introduction Early diagnosis of Alzheimer’s disease (AD) is important, because it enables patients and caregivers to ... |
| 5 | 0.6714 | `diag3.pdf` | Alzheimers/Diagnosis | 18 | disease. Pers. Med. Psychiatry, 2018, 7–8, 14-20. http://dx.doi.org/10.1016/j.pmip.2018.03.001 [78] Johnson, K.A.; Fox, ... |


---

## Observations


- **Source traceability**: Every result includes source filename, category, page number, and chunk ID.

- **Top-k behaviour**: All queries returned the requested number of results.

- **Qualitative relevance**: Results are topically aligned with queries (formal precision/recall metrics not computed — no labelled ground truth).


## Limitations


- Only Alzheimer's documents are indexed in Phase 6.

- Parkinson's queries will return Alzheimer's content (low relevance).

- No LLM synthesis — raw chunk excerpts returned as-is.

- Retrieval quality depends on PyMuPDF text extraction quality.
