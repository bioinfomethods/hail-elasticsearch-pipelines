import importlib.resources

PROJECTS_EXCLUDED_FROM_LOOKUP = {
    'R0555_seqr_demo',
    'R0607_gregor_training_project_',
    'R0608_gregor_training_project_',
    'R0801_gregor_training_project_',
    'R0811_gregor_training_project_',
    'R0812_gregor_training_project_',
    'R0813_gregor_training_project_',
    'R0814_gregor_training_project_',
    'R0815_gregor_training_project_',
    'R0816_gregor_training_project_',
}
GRCH37_TO_GRCH38_LIFTOVER_REF_PATH = importlib.resources.path(
    'v03_pipeline.var.liftover',
    'grch37_to_grch38.over.chain.gz',
)
GRCH38_TO_GRCH37_LIFTOVER_REF_PATH = importlib.resources.path(
    'v03_pipeline.var.liftover',
    'grch38_to_grch37.over.chain.gz',
)
