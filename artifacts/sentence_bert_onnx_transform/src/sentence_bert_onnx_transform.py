from pathlib import Path
import torch
from torch import nn
from torch.nn import functional as F
from transformers import AutoModel, AutoTokenizer
from typing import Optional
from typing_extensions import override
import argparse
import itertools
import sys
from contextlib import contextmanager
import threading


@contextmanager
def spinner(stdout: str) -> None:
    """Usage: with spinner("Loading model..."): ..."""

    class SpinnerThread(threading.Thread):
        def __init__(self, stdout: str) -> None:
            super().__init__()
            self.stdout = stdout
            self._stop_event = threading.Event()
            self._stop_event.clear()

        def run(self) -> None:
            for c in itertools.cycle(r"-\|/-\|/"):
                if self._stop_event.is_set():
                    break
                sys.stdout.write(f"\r{self.stdout} {c}")
                sys.stdout.flush()
                sys.stdout.write("\b" * (len(self.stdout) + 2))
                self._stop_event.wait(0.2)
            sys.stdout.write("\b" * (len(self.stdout) + 2))
            sys.stdout.flush()

    spinner_thread = SpinnerThread(stdout)
    spinner_thread.start()
    try:
        yield
    finally:
        spinner_thread._stop_event.set()
        spinner_thread.join()
        print()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_name", type=str, required=True)
    parser.add_argument("--output_model_path", type=str, required=True)
    parser.add_argument("--output_tokenizer_path", type=str, required=True)
    parser.add_argument(
        "--onnx-opset-version", type=int, default=13, help="ONNX opset version to use"
    )
    return parser.parse_args()


class SentenceBertOnnxModel(nn.Module):
    def __init__(self, model: AutoTokenizer) -> None:
        super().__init__()
        self._model = model

    def _mean_pooling(
        self, tokens_embeddings: torch.FloatTensor, attention_mask: torch.FloatTensor
    ) -> torch.FloatTensor:
        expanded_tokens_embeddings = tokens_embeddings * attention_mask.unsqueeze(-1)
        return torch.sum(expanded_tokens_embeddings, dim=1) / torch.clamp(
            torch.sum(attention_mask.to(torch.float), dim=1, keepdims=True),
            min=torch.finfo(expanded_tokens_embeddings.dtype).eps,
        )

    def _normalize(self, model_output: torch.FloatTensor) -> torch.FloatTensor:
        return F.normalize(model_output, p=2, dim=-1)

    @override
    def forward(
        self,
        input_ids: torch.LongTensor,
        attention_mask: torch.LongTensor,
        token_type_ids: Optional[torch.LongTensor] = None,
    ) -> torch.FloatTensor:
        model_output = self._model(
            input_ids=input_ids,
            attention_mask=attention_mask,
            token_type_ids=token_type_ids,
        ).last_hidden_state
        mean_pooled_output = self._mean_pooling(model_output, attention_mask)
        return self._normalize(mean_pooled_output)


def main(args: argparse.Namespace) -> None:
    with spinner(f"Loading model {args.model_name}..."):
        model: AutoModel = AutoModel.from_pretrained(args.model_name)
    with spinner(f"Loading tokenizer {args.model_name}..."):
        tokenizer: AutoTokenizer = AutoTokenizer.from_pretrained(args.model_name)
    torch_model = SentenceBertOnnxModel(model)
    torch_model.float().eval()
    with spinner(f"Exporting model to ONNX..."):
        dummy_tokenized_input = tokenizer(
            ["Hello World!"], return_tensors="pt", padding="max_length", truncation=True
        )
        tokenized_input_keys = list(dummy_tokenized_input.keys())
        output_model_path = Path(args.output_model_path)
        output_model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.onnx.export(
            torch_model.cpu(),
            tuple(dummy_tokenized_input[key] for key in tokenized_input_keys),
            args.output_model_path,
            input_names=tokenized_input_keys,
            output_names=["output"],
            do_constant_folding=True,
            dynamic_axes={
                **{
                    key: {0: "batch_size", 1: "sequence_length"}
                    for key in tokenized_input_keys
                },
                "output": {0: "batch_size"},
            },
            opset_version=args.onnx_opset_version,
        )
    with spinner(f"Saving tokenizer to {args.output_tokenizer_path}..."):
        output_tokenizer_path = Path(args.output_tokenizer_path)
        output_tokenizer_path.parent.mkdir(parents=True, exist_ok=True)
        tokenizer.save_pretrained(args.output_tokenizer_path)


if __name__ == "__main__":
    args = parse_args()
    main(args)
