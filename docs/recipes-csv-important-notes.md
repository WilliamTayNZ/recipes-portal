# Recipes CSV Important Notes



## Missing Values
How missing values are represented in the `recipes.csv` file.  

| Field                          | Missing Representation                                                                                   | Notes                                                                                |
|--------------------------------|----------------------------------------------------------------------------------------------------------|--------------------------------------------------------------------------------------|
| **Nutrition fields** (`Calories`, `FatContent`, `SaturatedFatContent`, `CholesterolContent`, `SodiumContent`, `CarbohydrateContent`, `FiberContent`, `SugarContent`, `ProteinContent`) | Always numeric. Missing values are represented as `0`.                                                   | Example: `...,0,0,0,...` for a recipe with no cholesterol, sodium, etc. Never `"NA"`. |
| **CookTime**, **PrepTime**, **TotalTime** | Always numeric strings (e.g. `"45"`, `"0"`).                                                             | No `"NA"`, no empty strings.                                                         |
| **RecipeYield** | `"NA"` when unknown. Otherwise, a free-text string like `"4 kebabs"` or `"1 bundt"`.                     |
| **Description** | NOT SURE                                                                                       |
| **Images** | NOT SURE                                                                                                 |
| **IngredientQuantities** | Always a list string. Individual elements inside the list may be `"NA"`. The whole column is never empty. |
| **IngredientParts** | NOT SURE | Smaller length than IngredientQuantities when IngredientQuantities has `"NA"` element
| **Instructions** | Always a list string of steps. Never `"NA"` or empty.                                                    |
| **RecipeServings** | Always a stringified number (e.g. `"4"`, `"12"`).                                                        |
| **AuthorName** / **RecipeCategory** | Always present and non-empty.                                                                            |

---

### IngredientQuantities and IngredientParts

From examining the dataset, the patterns for **`RecipeIngredientQuantities`** and **`RecipeIngredientParts`** are:

- **`Quantities`**: Can contain `"NA"` as a placeholder for missing quantity.  
- **`Parts`**: Never contains `"NA"`. Instead, the corresponding ingredient part is simply omitted, resulting in unequal list lengths.  

---

#### Examples from Recipes CSV

##### RecipeId **114** – *Chicken Breasts Saltimbocca*
```csv
"RecipeIngredientQuantities": "['6', '6', '6', '1/4', '1/4', '1', '1/2', '1/4', '1/3', '1', '1/2', '1/4', '1/4', 'NA']"

"RecipeIngredientParts":      "['boneless skinless chicken breast halves', 'ham slices', 'swiss cheese', 'all-purpose flour', 'parmesan cheese', 'salt', 'dried sage', 'pepper', 'dry white wine', 'cornstarch', 'water', 'rice']"
```

##### RecipeId **187** – *Chicken-Fried Steak With Cracked Pepper Gravy*
```csv
"RecipeIngredientQuantities": "['1 1/2', '1 1/2', '2', '1', '2', '1/2', '1/2', '2', '4', '1/4', '2', '1 1/3', 'NA', '1']"

"RecipeIngredientParts":     "['flour', 'salt', 'pepper', 'cayenne', 'eggs', 'bock beer', 'unsalted butter', 'flour', 'milk', 'salt', 'cracked pepper']"


