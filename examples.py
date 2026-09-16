"""
Примеры юниорских проектов для демонстрации калькулятора
"""


# Юниорский золотой проект (Невада, США)
JUNIOR_GOLD_NEVADA = {
    'name': 'Silver Peak Gold Project (Nevada, USA)',
    'commodity': 'Gold',
    'jurisdiction': 'USA (Tier-1)',
    'stage': 'PEA (Preliminary Economic Assessment)',
    
    # Геология
    'tonnage_m': 25.0,          # 25 млн тонн
    'grade': 2.5,               # 2.5 g/t Au
    'recovery': 0.92,           # 92% извлечение
    
    # Экономика
    'metal_price': 2000,        # $/oz Au
    'opex_per_ton': 35,         # $/тонна
    'capex_total': 180,         # $ млн
    'lom_years': 10,
    
    # Рынок
    'market_cap': 120,          # $ млн (текущая капитализация)
    'p_equilibrium': 1800,      # равновесная цена ($/oz)
    
    # Финансирование (типичное для юниора)
    'financing_structure': {
        'equity_junior': 0.70,      # 70% equity (высокий риск)
        'mezzanine': 0.20,          # 20% мезонин
        'royalty_streaming': 0.10,  # 10% стриминг
    },
    
    # Параметры
    'stated_ke': 0.15,
    'kd': 0.12,
    'tax_rate': 0.28,
    
    # Supply curve (цены безубыточности конкурентов, $/oz)
    'supply_curve': [800, 950, 1100, 1250, 1400, 1550, 1700, 1850, 2000, 2200]
}


# Юниорский медный проект (Чили)
JUNIOR_COPPER_CHILE = {
    'name': 'Andes Copper Project (Chile)',
    'commodity': 'Copper',
    'jurisdiction': 'Chile (Tier-1)',
    'stage': 'PFS (Pre-Feasibility Study)',
    
    # Геология
    'tonnage_m': 150.0,         # 150 млн тонн
    'grade': 0.0055,            # 0.55% Cu
    'recovery': 0.87,           # 87% извлечение
    
    # Экономика
    'metal_price': 8500,        # $/т Cu
    'opex_per_ton': 12,         # $/тонна
    'capex_total': 850,         # $ млн
    'lom_years': 18,
    
    # Рынок
    'market_cap': 450,          # $ млн
    'p_equilibrium': 7500,      # $/т
    
    # Финансирование
    'financing_structure': {
        'project_finance': 0.50,
        'equity_mid_tier': 0.30,
        'mezzanine': 0.20,
    },
    
    'stated_ke': 0.13,
    'kd': 0.09,
    'tax_rate': 0.27,
    
    'supply_curve': [4500, 5200, 5800, 6400, 7000, 7600, 8200, 8800, 9500, 10200]
}


# Юниорский литиевый проект (Аргентина)
JUNIOR_LITHIUM_ARGENTINA = {
    'name': 'Salta Lithium Brine (Argentina)',
    'commodity': 'Lithium (LCE)',
    'jurisdiction': 'Argentina (Tier-2)',
    'stage': 'Scoping Study',
    
    # Геология
    'tonnage_m': 80.0,          # 80 млн тонн рассола
    'grade': 0.00065,           # 650 ppm Li (0.065%)
    'recovery': 0.55,           # 55% извлечение (evaporation ponds)
    
    # Экономика
    'metal_price': 15000,       # $/т LCE
    'opex_per_ton': 8,          # $/тонна рассола
    'capex_total': 320,         # $ млн
    'lom_years': 25,
    
    # Рынок
    'market_cap': 180,          # $ млн
    'p_equilibrium': 12000,     # $/т
    
    # Финансирование (высокий риск юниора + юрисдикция)
    'financing_structure': {
        'equity_junior': 0.85,
        'royalty_streaming': 0.15,
    },
    
    'stated_ke': 0.18,
    'kd': 0.14,
    'tax_rate': 0.35,
    
    'supply_curve': [6000, 7500, 9000, 10500, 12000, 13500, 15000, 17000, 19000]
}


# Проблемный проект (с высоким риском Hard-Lock)
DISTRESSED_PROJECT = {
    'name': 'Deep Underground Gold (West Africa)',
    'commodity': 'Gold',
    'jurisdiction': 'West Africa (Tier-3)',
    'stage': 'PEA',
    
    'tonnage_m': 12.0,
    'grade': 3.8,
    'recovery': 0.85,
    
    'metal_price': 2000,
    'opex_per_ton': 65,         # высокие OPEX (глубокая шахта)
    'capex_total': 280,         # высокий CAPEX
    'lom_years': 8,
    
    'market_cap': 95,
    'p_equilibrium': 1800,
    
    'financing_structure': {
        'equity_junior': 0.90,
        'mezzanine': 0.10,
    },
    
    'stated_ke': 0.20,
    'kd': 0.16,
    'tax_rate': 0.30,
    
    'supply_curve': [900, 1100, 1300, 1500, 1700, 1900, 2100, 2300, 2500]
}


ALL_EXAMPLES = {
    'Silver Peak Gold (Nevada)': JUNIOR_GOLD_NEVADA,
    'Andes Copper (Chile)': JUNIOR_COPPER_CHILE,
    'Salta Lithium (Argentina)': JUNIOR_LITHIUM_ARGENTINA,
    'Deep Underground Gold (West Africa) [DISTRESSED]': DISTRESSED_PROJECT,
}