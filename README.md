# Best Paper Awards in Computer Science (since 1996)
I rebuilt [Jeff Huang's website](https://jeffhuang.com/best_paper_awards.html) such that it'll be easier for contributors to add new papers or top conferences.
Ideally this will help to maintain the website and keep it up-to-date.

## Installation
```python
pip3 install yattag
```

## Usage
```bash
cat rawBpa | python3 generate_html.py > index.html
```

## Demo
https://wgierke.github.io/best_paper_awards

## Format
`rawBpa` contains the data about the best papers in the format
```
conference_lower_abbreviation, conference_name (conference_topic)
 paper_year, paper_url, paper_title
  author_name, author_institution
 ```
such as
```
icml, ICML (Machine Learning)
 2019, https://arxiv.org/abs/1811.12359, Challenging Common Assumptions in the Unsupervised Learning of Disentangled Representations
  Francesco Locatello ETH Zurich, Max-Planck Institute for Intelligent Systems
 ```
