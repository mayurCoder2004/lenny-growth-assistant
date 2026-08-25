# Local LLM Debug Transcript

## Configuration

The local generation path uses Ollama through `backend/app/llm/ollama_provider.py`.

Default configuration:

- `LLM_PROVIDER=ollama`
- `OLLAMA_BASE_URL=http://localhost:11434`
- `OLLAMA_MODEL=qwen2.5:1.5b`

The local model was run with a 4096-token context during development. The provider uses a low temperature and extended read timeout to make local generation more stable.

## Observations

`qwen2.5:1.5b` is small and practical for local evaluation, but it has constraints:

- Generation latency is noticeable, especially on CPU.
- Long essay outputs are weaker and slower than short answers.
- Structured JSON can fail if prompts are too complex.
- Long transcript excerpts increase the chance of truncation or drift.

## Prompt/Context Adjustments

The Ship30 essay target was reduced from around 1250 words to approximately 700 words. This made local generation more realistic for `qwen2.5:1.5b`.

`Ship30Skill._build_prompt()` truncates each evidence chunk with `item.content[:3500]` before sending it to the LLM. This keeps selected transcript context useful without overwhelming the local model.

## Result

Local Ollama support remains the default path. The documentation should set evaluator expectations clearly: local generation works, but larger/cloud models may produce better long-form quality and more reliable structured output.
