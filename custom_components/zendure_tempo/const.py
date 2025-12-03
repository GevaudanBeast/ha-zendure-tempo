"""Constants for Zendure Tempo integration."""

DOMAIN = "zendure_tempo"

# Default values
DEFAULT_SOC_ROUGE = 100
DEFAULT_SOC_ROUGE_SOLEIL = 80  # SOC reduced when solar expected
DEFAULT_SOC_NORMAL = 90
DEFAULT_INPUT_LIMIT = 1200
DEFAULT_OUTPUT_LIMIT = 1200
DEFAULT_SOLAR_THRESHOLD = 3.0  # kWh - minimum solar to reduce charge
DEFAULT_ENABLED_ROUGE = True
DEFAULT_ENABLED_BLANC = True
DEFAULT_ENABLED_BLEU = False  # Disabled by default for blue days

# Entity IDs (to be configured)
CONF_TEMPO_COLOR = "tempo_color_entity"
CONF_TEMPO_NEXT_COLOR = "tempo_next_color_entity"
CONF_TEMPO_HC = "tempo_hc_entity"
CONF_HYPER_INPUT_LIMIT = "hyper_input_limit_entity"
CONF_HYPER_OUTPUT_LIMIT = "hyper_output_limit_entity"
CONF_HYPER_SOC_SET = "hyper_soc_set_entity"
CONF_TEMPO_JOURS_ROUGE = "tempo_jours_rouge_entity"
CONF_TEMPO_JOURS_BLANC = "tempo_jours_blanc_entity"
CONF_SOLAR_FORECAST = "solar_forecast_entity"  # Optional

# Tempo colors
COLOR_BLEU = "Bleu"
COLOR_BLANC = "Blanc"
COLOR_ROUGE = "Rouge"

# Modes
MODE_ROUGE_HP = "Rouge HP - Décharge"
MODE_ROUGE_HC = "Rouge HC - Charge"
MODE_BLANC_HP = "Blanc HP - Décharge"
MODE_BLANC_HC = "Blanc HC - Normal"
MODE_VEILLE_ROUGE = "Veille Rouge - Charge"
MODE_BLEU = "Bleu - Normal"
MODE_DISABLED = "Désactivé"
