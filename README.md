# Advanced Track: Nexlevr AI Red Team Internship

My completed **Advanced track** for the [Nexlevr AI Red Team internship](https://www.nexlevr.app/resources/ai-red-team/advanced). It continues the testing of the BeanBox support bot from my [Beginner](https://github.com/khalilosss11/Beginner-Track) and [Intermediate](https://github.com/khalilosss11/Intermediate-Track) tracks.

| # | Quest | What I did | Headline result |
|---|---|---|---|
| 1 | [**Full AI product test**](quest-1-full-product-test/) | 35 multi-turn conversations (long chats, role-play, unusual formats, edge cases) × 3 runs = **105 real conversations**, graded by a second model and reviewed by hand. Findings report with severity ratings. | **0 Critical, 0 High.** 2 Medium: a role-play "training" request rebuilt the whole system prompt (3/3), and deadline maths from today's date still misleads. Discount attacks failed 18/18. |
| 2 | [**Automated testing pipeline**](quest-2-testing-pipeline/) | Pipeline that generates 51 tests (rule-based answers plus model-written attacks), runs them on 7 prompt/model versions, scores them and tracks pass rates in CSV, XLSX and a chart. **1,224 replies scored over 2 runs.** | Pass rate rose from **72.5% (v1)** to **95.1% (v5 Haiku)** and **100% (v5 Sonnet)**. It caught a **regression**: v4 fixed wellbeing but broke billing answers, and v5 fixed that. |

## Repository layout

```text
Advanced-Track/
├── tools/
│   ├── run_conversations.py        # multi-turn runner + grader (Quest 1)
│   └── summarize_conversations.py  # pass rates, failures, transcripts
├── quest-1-full-product-test/
│   ├── README.md                   # findings report with severity ratings
│   ├── build_conversations.py      # the 35 test conversations
│   ├── target/beanbox_v3.txt       # version under test
│   ├── review.json                 # manual verdicts that override the grader
│   ├── transcripts.md              # all 105 conversations
│   └── results/results.jsonl
├── quest-2-testing-pipeline/
│   ├── README.md                   # pipeline design and results
│   ├── pipeline.py                 # generate -> run -> score -> report
│   ├── versions.json               # prompt + model versions tracked
│   ├── prompts/                    # beanbox_v1.txt to beanbox_v5.txt
│   ├── tests/                      # generated test set and attacks
│   └── results/                    # history.csv, by_category.csv, latest.csv, pass_rates.xlsx, pass_rate.svg, runs/
    (quest-2-testing-pipeline/ci/eval-pipeline.yml: GitHub Actions template)
```

## Setup

- **Model under test:** Claude Haiku 5.5 (Claude Sonnet 5.5 for the model comparison in Quest 2). Every call is a fresh chat with no tools; multi-turn tests resume the same chat session.
- **Grader and attack generator:** Claude Sonnet 5.5.
- **Requirements:** Python 3.10+ and `openpyxl` (for the XLSX export only).
