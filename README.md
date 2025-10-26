# PolyView

- **Provide supporting and opposing facts to key findings in report (or white paper).**

## Usage

- **Input**: report (or white paper) in PPT or PDF format
- **Output**: Supporting and opposing facts and links for key findings in every page.

## Pipeline

| # | Stage                                       | Current Method                                                                                                                                                                                                  | Refinement Prospect                                             |
|---|---------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------|
| 1 | **Text Extraction**                         | **Currently uses MinerU 2.5**<br/> LlamaIndex > MinerU 2.5 > Docling                                                                                                                                            | ...                                                             |
| 2 | **Key Finding Extraction**                  | **Method 1:** OpenAI API<br/>**Method 2:** Add ordering tags to each sentence `<1> sentence1 </1> <2> sentence2 </2> ... <n> sentence n </n>`, then use trained 1B SLM to extract ordering tags of key findings | SLM can be further distilled                                    |
| 3 | **Query Generation** | **Method 1:** OpenAI API<br/>**Method 2:** Trained 1B SLM using modified GRPO                                                                                                                                   | Ongoing                                                         |
| 4 | **Search**                                  | Tavily or Serper API                                                                                                                                                                                            | These API still a bit lacking, need to look for better options. |
| 5 | **Search Result Ranking**                   | **Method 1:** OpenAI API<br/>**Method 2:** Trained 1B  SLM  reward model                                                                                                                                        | SLM can be further distilled                                    |
| 6 | **Output**                                  | Supporting and opposing facts with links in txt and Json format                                                                                                                                                 | ...                                                             |


## Model Training

### 1️⃣ Model for Key Finding Extraction

Extracts key findings from documents with sentence-level precision.

- **Training:** LLM annotation + human correction
- **Input:** `<1>sentence1</1><2>sentence2</2>...<n>sentence n</n>`
- **Output:** `[[1,3], [5,5], [10,14]]` (sentence index ranges)
- **Next Step:** Expand to multi-industry datasets

### 2️⃣ Reward Model (Ranking Model)

Ranks search results by relevance to findings (support/oppose).

- **Training:** LLM-generated statements in various styles
- **Input:** `<finding>...</finding><web>...</web>`
- **Output:** Dual binary classification (0/1 for support/oppose)
- **Next Step:** Persona-diverse data, advanced hard negative mining

### 3️⃣ Query Generation Model (🚧Ongoing)

- Train SLM to generate search queries
- Retrieve search results (3 per rollout) using generated queries
- Score results using reward model
- Optimize using GRPO with 8 rollouts per prompt

**GRPO Modifications for Better Exploration:**
- ⬆️ **Temperature = 2.0** & **3 - 4 for first token** → diverse queries
- ✂️ **Clip range = 1.4** → foster exploration
- ❌ **Remove token count division** → prevent short correct query or wrong query which is overly long
- ✂️ **Clip `(π/π_ref) × advantage` on 95th percentile** → stabilize training (prevent extreme negatives), especially during early phase
- ...

**Next Step:** Query Decompostion, Multi-Agent Training, 

## Prerequisites

- Python 3.11+
- Docker and Docker Compose (for containerized deployment)
- OpenAI API Key
- Serper API Key (get free credits at [serper.dev](https://serper.dev))

## Setup

### Local Setup

1. Clone the repository:
```bash
git clone 
cd PolyView
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

5. Run the application:
```bash
# Place your file in the input folder
# Run minerU to extract text and images, install minerU beforehand.
# Modify filename in main.py file
mineru -p [input folder or file] -o [output folder or file]
python main.py
# Check out the result in the output folder
```

### Docker Setup

1. Set up environment variables:
```bash
cp .env.example .env
# Edit .env and add your API keys
```

2. Build and run with Docker Compose:
```bash
docker-compose up --build
```


## Usage

Edit `main.py` to customize the research subject:

```python
if __name__ == "__main__":
    subject = "Your research subject here"
    industry = "Your research industry here"
    agent_system_init = run_research_report()
    result = agent_system_init.run(subject,industry)
```
