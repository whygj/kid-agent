"""Built-in capability class paths."""

BUILTIN_CAPABILITY_CLASSES: dict[str, str] = {
    "chat": "kid_agent.capabilities.chat:ChatCapability",
    "deep_solve": "kid_agent.capabilities.deep_solve:DeepSolveCapability",
    "deep_question": "kid_agent.capabilities.deep_question:DeepQuestionCapability",
    "deep_research": "kid_agent.capabilities.deep_research:DeepResearchCapability",
    "math_animator": "kid_agent.capabilities.math_animator:MathAnimatorCapability",
    "visualize": "kid_agent.capabilities.visualize:VisualizeCapability",

    "kid_tutor": "kid_agent.capabilities.kid_tutor:KidTutorCapability",  # kid-agent特色
}