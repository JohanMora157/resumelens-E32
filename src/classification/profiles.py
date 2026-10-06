"""Definición de los 4 perfiles profesionales de ResumeLens.

Cada perfil tiene:
  - canonical_order: orden de las categorías (el sorter y los autómatas lo siguen).
  - categories: qué skills CANÓNICAS (salida del FST) pertenecen a cada categoría.

REGLAS DEL VOCABULARIO (para los 3):
  1. Los tokens son exactamente los que emite el FST (data/aliases.json).
  2. Dentro de UN perfil, un token pertenece a UNA sola categoría.
  3. Un mismo token puede cambiar de categoría entre perfiles
     (SQL es DATABASE en Full Stack y QUERY_LANGUAGE en Data Analyst).
  4. Si un token no está en el perfil, el sorter lo descarta.
"""

FULL_STACK_DEVELOPER = {
    "canonical_order": ["LANGUAGE", "FRONTEND", "BACKEND", "DATABASE", "API", "VERSION_CONTROL"],
    "categories": {
        "LANGUAGE": ["JAVASCRIPT", "TYPESCRIPT"],
        "FRONTEND": ["REACT", "ANGULAR", "VUE"],
        "BACKEND": ["NODE_JS", "DJANGO", "SPRING_BOOT"],
        "DATABASE": ["SQL", "POSTGRESQL", "MYSQL", "MONGODB"],
        "API": ["REST_API"],
        "VERSION_CONTROL": ["GIT"],
    },
}

MACHINE_LEARNING_ENGINEER = {
    "canonical_order": [
        "LANGUAGE", "DATA_PROCESSING", "ML_LIBRARY",
        "MODEL_FRAMEWORK", "DATABASE", "VERSION_CONTROL",
    ],
    "categories": {
        "LANGUAGE": ["PYTHON"],
        "DATA_PROCESSING": ["PANDAS", "NUMPY"],
        "ML_LIBRARY": ["SCIKIT_LEARN"],
        "MODEL_FRAMEWORK": ["TENSORFLOW", "PYTORCH"],
        "DATABASE": ["SQL", "POSTGRESQL", "MYSQL"],
        "VERSION_CONTROL": ["GIT"],
    },
}

QA_ENGINEER = {
    "canonical_order": [
        "TESTING", "TEST_AUTOMATION", "API_TESTING",
        "PROGRAMMING", "ISSUE_TRACKING", "VERSION_CONTROL",
    ],
    "categories": {
        "TESTING": ["PYTEST", "JUNIT", "TESTNG"],
        "TEST_AUTOMATION": ["SELENIUM", "CYPRESS", "PLAYWRIGHT"],
        "API_TESTING": ["POSTMAN", "REST_ASSURED"],
        "PROGRAMMING": ["PYTHON", "JAVA", "JAVASCRIPT"],
        "ISSUE_TRACKING": ["JIRA"],
        "VERSION_CONTROL": ["GIT"],
    },
}

DATA_ANALYST = {
    "canonical_order": [
        "QUERY_LANGUAGE", "SPREADSHEET", "ANALYSIS_LANGUAGE",
        "DATA_PROCESSING", "VISUALIZATION",
    ],
    "categories": {
        "QUERY_LANGUAGE": ["SQL", "POSTGRESQL", "MYSQL"],
        "SPREADSHEET": ["EXCEL"],
        "ANALYSIS_LANGUAGE": ["PYTHON", "R"],
        "DATA_PROCESSING": ["PANDAS", "NUMPY"],
        "VISUALIZATION": ["POWER_BI", "TABLEAU", "MATPLOTLIB"],
    },
}

PROFILES = {
    "FULL_STACK_DEVELOPER": FULL_STACK_DEVELOPER,
    "MACHINE_LEARNING_ENGINEER": MACHINE_LEARNING_ENGINEER,
    "QA_ENGINEER": QA_ENGINEER,
    "DATA_ANALYST": DATA_ANALYST,
}