# Error Log & Fixes — Smart Study Assistant

## 1. Deprecated Package Warning
| | |
|---|---|
| **Error** | `google.generativeai` package is deprecated, no longer receiving updates |
| **Fix** | Switched from `google-generativeai` to `google-genai` in `requirements.txt` and rewrote `utils/gemini.py` to use the new `genai.Client()` API |

## 2. Import Error — `google-genai`
| | |
|---|---|
| **Error** | `ImportError: cannot import name 'genai' from 'google'` |
| **Cause** | Old `google-generativeai` package was still installed, causing a namespace conflict |
| **Fix** | Uninstalled `google-generativeai` from the venv, then installed `google-genai` cleanly |

## 3. Model Not Found — `gemini-1.5-flash`
| | |
|---|---|
| **Error** | `404 NOT_FOUND: models/gemini-1.5-flash is not found for API version v1beta` |
| **Fix** | Updated model to `gemini-2.0-flash` (1.5-flash was retired) |

## 4. Quota Exhausted — Gemini Free Tier
| | |
|---|---|
| **Error** | `429 RESOURCE_EXHAUSTED: You exceeded your current quota` (limit: 0) |
| **Cause** | Gemini API free-tier daily quota fully exhausted |
| **Fix** | Migrated to **OpenRouter** API, which aggregates multiple model providers |

## 5. OpenRouter Privacy Policy Block
| | |
|---|---|
| **Error** | `404: No endpoints available matching your guardrail restrictions and data policy` |
| **Fix** | Updated privacy settings at [openrouter.ai/settings/privacy](https://openrouter.ai/settings/privacy) to allow data sharing (required by free models). Also added `HTTP-Referer` and `X-Title` headers to the API client |

## 6. Rate Limiting — Free Models
| | |
|---|---|
| **Error** | `429: model is temporarily rate-limited upstream` (hit on multiple models) |
| **Fix** | Added **automatic model fallback** — if one model returns 429, the code tries the next model in a list |

## 7. Model Not Found — OpenRouter
| | |
|---|---|
| **Error** | `404: No endpoints found for meta-llama/llama-3.1-8b-instruct:free` and `deepseek/deepseek-chat-v3-0324:free` |
| **Cause** | Model IDs were guessed and didn't exist on OpenRouter |
| **Fix** | Queried the live OpenRouter API (`client.models.list()`) to get verified available free models. Also updated fallback logic to catch **both 404 and 429** errors |

## 8. Migration to Cerebras AI
| | |
|---|---|
| **Problem** | OpenRouter free-tier latency was high and availability was inconsistent. |
| **Fix** | Migrated to **Cerebras AI** for extremely fast, OpenAI-compatible inference. Updated `utils/gemini.py` with the Cerebras base URL (`https://api.cerebras.ai/v1`) and added models `llama3.1-8b` and `gpt-oss-120b`. |

## 9. Quiz JSON Parsing Error
| | |
|---|---|
| **Error** | `json.JSONDecodeError: Expecting value: line 1 column 1 (char 0)` |
| **Cause** | The LLM sometimes wrapped its JSON response in markdown code blocks (e.g., ` ```json ... ``` `) or added conversational text before/after the JSON array. |
| **Fix** | Implemented a robust **defensive parser** using `re.sub` and `re.search` to strip away code fences and extract ONLY the `[...]` JSON array from the raw AI response. |

## 10. Radio Selection Index Error
| | |
|---|---|
| **Error** | `ValueError: None is not in list` in `app.py` |
| **Cause** | When `st.radio` was in its initial unselected state (`index=None`), it returned `None`. The code was attempting to run `.index(None)` on the list of options. |
| **Fix** | Added a **guard clause** (`if user_choice is not None:`) in the quiz loop to only attempt session state updates once a student actually selects an option. |