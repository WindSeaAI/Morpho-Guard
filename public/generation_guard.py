"""Intervene on the generated prefix of a single greedy continuation."""

from transformers import LogitsProcessor

if __package__:
    from .morpho_guard import evaluate_gate
else:
    from morpho_guard import evaluate_gate


class GenerationGuard(LogitsProcessor):
    def __init__(self, tokenizer, prompt_length, eos_id):
        self.tokenizer = tokenizer
        self.prompt_length = prompt_length
        self.refusal = tokenizer.encode(
            "\n\nI cannot continue with this request.", add_special_tokens=False
        )
        if not self.refusal:
            raise ValueError("Refusal must tokenize to at least one token")
        self.refusal.append(eos_id)
        self.trigger_step = None

    def __call__(self, input_ids, scores):
        if input_ids.shape[0] != 1:
            raise ValueError("GenerationGuard requires one sequence and one beam")
        step = input_ids.shape[-1] - self.prompt_length
        if self.trigger_step is None:
            if step == 0:
                return scores
            prefix = self.tokenizer.decode(
                input_ids[0, self.prompt_length:].tolist(), skip_special_tokens=True
            )
            if not prefix.strip() or not evaluate_gate(prefix)["triggered"]:
                return scores
            self.trigger_step = step
        offset = min(step - self.trigger_step, len(self.refusal) - 1)
        masked = scores.new_full(scores.shape, float("-inf"))
        masked[0, self.refusal[offset]] = 0
        return masked
