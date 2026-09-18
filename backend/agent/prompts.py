"""Prompt contracts are rendered from CustomerAgentContext — never from a mega data-pack dump."""

from agent.context import render_extract_prompt, render_respond_prompt

__all__ = ["render_extract_prompt", "render_respond_prompt"]
