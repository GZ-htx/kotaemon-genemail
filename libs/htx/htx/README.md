## HTX modules

### `components`

- `long_context.py`: contains functions for storing the txt file when a file is uploaded by user and a function to get the text from a .txt file

### `db`

- `base_models.py`: contains the structure of the 3 new tables: `Customer`, `TenderType`, `SchedaPrompt`
- `models.py`: imports `base_models.py` and creates the tables in the database

### `pages`

- `__init__.py`: initializes the tabs for T&B Tab
- `customer.py`: contains the CRUD for the `Customer` table
- `scheda_prompt.py`: contains the CRUD for the `SchedaPrompt` table
- `tender_type.py`: contains the CRUD for the `TenderType` table

### `pipelines`

- `answer_long_context.py`: defines the class which is responsible for answering when a Long Context method is used.
- `long_context_retrieval.py`: defines the class which is responsible for retrieving a single document containing the whole txt file when a Long Context method is used.

### `reasoning`

- `genemail.py`: pipeline for the GenEmail reasoning method
- `genemaillc.py`: pipeline for the GenEmail Long Context reasoning method
- `genscheda.py`: pipeline for the GenScheda reasoning method
- `genschedalc.py`: pipeline for the GenScheda Long Context reasoning method
- `simplelc.py`: pipeline for the Simple Long Context reasoning method

### `service`

- `customer.py`: contains the functions useful to interact with the `Customer` table
- `scheda_prompt.py`: contains the functions useful to interact with the `SchedaPrompt` table
- `tender_type.py`: contains the functions useful to interact with the `TenderType` table

### `other files`

- `explanations.py`: contains the values of the explanations for the T&B Tab