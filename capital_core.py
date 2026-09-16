"""
Ω-CAPITAL CORE ENGINE
Реализация ключевых принципов патента Ω-CAPITAL v2.0:
- True CoC (истинная стоимость капитала)
- NAV-премия и effective WACC
- Capital Hard-Lock
- Supply curve positioning
"""

import numpy as np
import pandas as pd
from scipy import stats
from typing import Dict, Tuple, Optional


class CapitalCalculator:
    """Основной калькулятор оценки юниорского проекта"""
    
    def __init__(self):
        # Стандартные ставки инструментов финансирования (годовые %)
        self.instrument_rates = {
            'IG_senior_debt': 0.075,       # 7.5%
            'sub_IG_senior_debt': 0.105,   # 10.5%
            'project_finance': 0.115,      # 11.5%
            'junior_senior_debt': 0.135,   # 13.5%
            'mezzanine': 0.18,             # 18.0%
            'royalty_streaming': 0.22,     # 22.0%
            'convertible_bonds': 0.12,     # 12.0%
            'preferred_equity': 0.20,      # 20.0%
            'equity_major': 0.12,          # 12.0%
            'equity_mid_tier': 0.17,       # 17.0%
            'equity_junior': 0.30,         # 30.0% (высокий риск)
        }
    
    def calculate_true_coc(self, financing_structure: Dict[str, float]) -> float:
        """
        ЭТАП 2 патента Ω-CAPITAL: Расчёт истинной стоимости капитала
        True_CoC = Σ (weight_i × cost_i)
        
        Args:
            financing_structure: словарь {instrument: weight}, где weight в [0,1]
        
        Returns:
            True CoC в виде десятичной дроби (например, 0.123 = 12.3%)
        """
        if abs(sum(financing_structure.values()) - 1.0) > 0.01:
            raise ValueError("Сумма весов финансирования должна быть равна 1.0")
        
        true_coc = 0.0
        for instrument, weight in financing_structure.items():
            if instrument not in self.instrument_rates:
                raise ValueError(f"Неизвестный инструмент: {instrument}")
            true_coc += weight * self.instrument_rates[instrument]
        
        return true_coc
    
    def calculate_nav(self, 
                     tonnage_m: float,
                     grade: float,
                     recovery: float,
                     metal_price: float,
                     opex_per_ton: float,
                     capex_total: float,
                     lom_years: int,
                     discount_rate: float) -> float:
        """
        Расчёт NAV (Net Asset Value) через упрощённый DCF
        
        Args:
            tonnage_m: ресурсы/запасы в млн тонн
            grade: содержание (например, 0.005 = 0.5% Cu или 1.5 g/t Au)
            recovery: металлургическое извлечение (0-1)
            metal_price: цена металла ($/т или $/oz)
            opex_per_ton: операционные затраты ($/тонна руды)
            capex_total: капитальные затраты ($ млн)
            lom_years: срок жизни рудника (лет)
            discount_rate: ставка дисконтирования (True CoC)
        
        Returns:
            NAV в $ млн
        """
        # Годовая добыча металла
        annual_production_ton = tonnage_m * 1e6 * grade * recovery / lom_years
        
        # Конвертация в нужные единицы (для Au в oz, для Cu в lb)
        # Предполагаем, что metal_price уже в нужных единицах
        annual_revenue = annual_production_ton * metal_price / 1e6  # $ млн
        annual_opex = tonnage_m * 1e6 / lom_years * opex_per_ton / 1e6  # $ млн
        
        # Годовой CAPEX (равномерное распределение по LoM, первые 3 года)
        capex_years = min(3, lom_years)
        annual_capex = capex_total / capex_years
        
        # Расчёт NPV
        npv = -capex_total  # начальные инвестиции
        
        for year in range(1, lom_years + 1):
            if year <= capex_years:
                capex = annual_capex
            else:
                capex = 0
            
            fcf = annual_revenue - annual_opex - capex
            npv += fcf / ((1 + discount_rate) ** year)
        
        return npv
    
    def calculate_nav_multiple(self, market_cap: float, nav: float) -> float:
        """ЭТАП 3: NAV-multiple = Market_Cap / NAV"""
        if nav == 0:
            return float('inf')
        return market_cap / nav
    
    def calculate_effective_wacc(self,
                                stated_ke: float,
                                nav_multiple: float,
                                w_equity: float,
                                w_debt: float,
                                kd: float,
                                tax_rate: float) -> float:
        """
        ЭТАП 3: Расчёт effective WACC с учётом NAV-премии
        """
        premium_factor = 1.0 / nav_multiple if nav_multiple != 0 else 1.0
        effective_ke = stated_ke * premium_factor
        effective_wacc = w_equity * effective_ke + w_debt * kd * (1 - tax_rate)
        return effective_wacc
    
    def calculate_p_breakeven(self,
                              opex_per_ton: float,
                              capex_amort: float,
                              true_coc: float,
                              capital: float,
                              recovery: float,
                              grade: float,
                              tonnage_m: float) -> float:
        """
        ЭТАП 57: Цена безубыточности
        P_breakeven = (OPEX + CAPEX_amort + True_CoC × Capital) / (Recovery × Grade × Tonnage)
        """
        total_cost = opex_per_ton + capex_amort + true_coc * capital
        denominator = recovery * grade * tonnage_m * 1e6
        if denominator == 0:
            return float('inf')
        return total_cost / denominator * 1e6  # в тех же единицах, что metal_price
    
    def calculate_supply_quartile(self, 
                                  p_breakeven: float,
                                  supply_curve: list) -> int:
        """
        ЭТАП 57: Позиционирование на кривой предложения
        """
        if not supply_curve:
            return 2  # по умолчанию средний квартиль
        
        rank = sum(1 for p in supply_curve if p <= p_breakeven)
        quartile = int(np.ceil(4 * rank / len(supply_curve)))
        return min(max(quartile, 1), 4)
    
    def calculate_irr(self, cashflows: list) -> float:
        """Упрощённый расчёт IRR через numpy"""
        try:
            return np.irr(cashflows) if hasattr(np, 'irr') else self._irr_manual(cashflows)
        except:
            return self._irr_manual(cashflows)
    
    def _irr_manual(self, cashflows: list, tol=1e-6, maxiter=1000) -> float:
        """Ручной расчёт IRR методом Ньютона"""
        rate = 0.1
        for _ in range(maxiter):
            npv = sum(cf / ((1 + rate) ** t) for t, cf in enumerate(cashflows))
            d_npv = sum(-t * cf / ((1 + rate) ** (t + 1)) for t, cf in enumerate(cashflows))
            if abs(d_npv) < 1e-12:
                break
            new_rate = rate - npv / d_npv
            if abs(new_rate - rate) < tol:
                return new_rate
            rate = new_rate
        return rate
    
    def capital_hard_lock_check(self,
                                irr: float,
                                true_coc: float,
                                p_breakeven: float,
                                p_equilibrium: float) -> Dict:
        """
        ЭТАП 34 патента Ω-CAPITAL: Capital Hard-Lock
        if (IRR_project < True_CoC) or (P_breakeven > P_equilibrium × 1.1):
            Capital_Hard_Lock = TRUE
        """
        irr_condition = irr < true_coc
        price_condition = p_breakeven > p_equilibrium * 1.1
        
        hard_lock = irr_condition or price_condition
        
        reasons = []
        if irr_condition:
            reasons.append(f"IRR ({irr:.2%}) < True_CoC ({true_coc:.2%})")
        if price_condition:
            reasons.append(
                f"P_breakeven ({p_breakeven:.2f}) > P_equilibrium × 1.1 ({p_equilibrium * 1.1:.2f})"
            )
        
        return {
            'hard_lock': hard_lock,
            'irr_condition': irr_condition,
            'price_condition': price_condition,
            'reasons': reasons,
            'recommendation': 'BLOCK' if hard_lock else 'SANCTION'
        }
    
    def full_valuation(self, project_data: Dict) -> Dict:
        """
        Полная оценка проекта по методологии Ω-CAPITAL
        
        Args:
            project_data: словарь со всеми параметрами проекта
        
        Returns:
            Словарь с результатами оценки
        """
        # 1. True CoC
        true_coc = self.calculate_true_coc(project_data['financing_structure'])
        
        # 2. NAV
        nav = self.calculate_nav(
            tonnage_m=project_data['tonnage_m'],
            grade=project_data['grade'],
            recovery=project_data['recovery'],
            metal_price=project_data['metal_price'],
            opex_per_ton=project_data['opex_per_ton'],
            capex_total=project_data['capex_total'],
            lom_years=project_data['lom_years'],
            discount_rate=true_coc
        )
        
        # 3. NAV-multiple
        nav_multiple = self.calculate_nav_multiple(
            project_data['market_cap'], nav
        )
        
        # 4. Effective WACC
        effective_wacc = self.calculate_effective_wacc(
            stated_ke=project_data.get('stated_ke', 0.12),
            nav_multiple=nav_multiple,
            w_equity=project_data['financing_structure'].get('equity_junior', 0) +
                     project_data['financing_structure'].get('equity_mid_tier', 0) +
                     project_data['financing_structure'].get('equity_major', 0),
            w_debt=sum(v for k, v in project_data['financing_structure'].items() 
                      if 'debt' in k.lower()),
            kd=project_data.get('kd', 0.10),
            tax_rate=project_data.get('tax_rate', 0.30)
        )
        
        # 5. P_breakeven
        p_breakeven = self.calculate_p_breakeven(
            opex_per_ton=project_data['opex_per_ton'],
            capex_amort=project_data['capex_total'] / project_data['lom_years'],
            true_coc=true_coc,
            capital=project_data['capex_total'],
            recovery=project_data['recovery'],
            grade=project_data['grade'],
            tonnage_m=project_data['tonnage_m']
        )
        
        # 6. Supply quartile
        supply_quartile = self.calculate_supply_quartile(
            p_breakeven,
            project_data.get('supply_curve', [])
        )
        
        # 7. IRR (упрощённый)
        cashflows = [-project_data['capex_total']]
        for year in range(1, project_data['lom_years'] + 1):
            revenue = (project_data['tonnage_m'] * 1e6 * 
                      project_data['grade'] * project_data['recovery'] / 
                      project_data['lom_years'] * project_data['metal_price'] / 1e6)
            opex = project_data['tonnage_m'] * 1e6 / project_data['lom_years'] * \
                   project_data['opex_per_ton'] / 1e6
            cashflows.append(revenue - opex)
        
        irr = self.calculate_irr(cashflows)
        
        # 8. Capital Hard-Lock
        hard_lock_result = self.capital_hard_lock_check(
            irr=irr,
            true_coc=true_coc,
            p_breakeven=p_breakeven,
            p_equilibrium=project_data.get('p_equilibrium', 
                                           project_data['metal_price'] * 0.8)
        )
        
        # 9. Вердикт
        if nav_multiple < 0.8:
            verdict = "НЕДООЦЕНКА (BUY)"
            verdict_color = "green"
        elif nav_multiple > 1.3:
            verdict = "ПЕРЕОЦЕНКА (SELL/SHORT)"
            verdict_color = "red"
        else:
            verdict = "СПРАВЕДЛИВАЯ ОЦЕНКА (HOLD)"
            verdict_color = "yellow"
        
        return {
            'true_coc': true_coc,
            'nav': nav,
            'nav_multiple': nav_multiple,
            'effective_wacc': effective_wacc,
            'p_breakeven': p_breakeven,
            'supply_quartile': supply_quartile,
            'irr': irr,
            'hard_lock': hard_lock_result,
            'verdict': verdict,
            'verdict_color': verdict_color,
            'cashflows': cashflows,
        }


# Глобальный экземпляр калькулятора
calculator = CapitalCalculator()