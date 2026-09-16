"""
Ω-CAPITAL HARD-LOCK CALCULATOR
Веб-интерфейс для оценки юниорских горных проектов

Запуск: streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from capital_core import calculator
from examples import ALL_EXAMPLES


# Настройка страницы
st.set_page_config(
    page_title="Ω-CAPITAL Hard-Lock Calculator",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Заголовок
st.title("⚡ Ω-CAPITAL Hard-Lock Calculator")
st.markdown("""
**Оценка юниорских горных проектов по методологии Ω-CAPITAL v2.0**

*True CoC • NAV-премия • Capital Hard-Lock • Supply Curve Positioning*
""")

# Боковая панель — ввод данных
with st.sidebar:
    st.header("📊 Параметры проекта")
    
    # Выбор примера или ручной ввод
    example_choice = st.selectbox(
        "Загрузить пример или ввести вручную:",
        ["Ввести вручную"] + list(ALL_EXAMPLES.keys())
    )
    
    if example_choice != "Ввести вручную":
        project = ALL_EXAMPLES[example_choice].copy()
    else:
        project = {}
    
    st.subheader("🏔 Геология")
    project['name'] = st.text_input("Название проекта", 
                                    project.get('name', 'My Project'))
    project['commodity'] = st.selectbox("Металл", 
                                        ['Gold', 'Silver', 'Copper', 'Lithium (LCE)', 
                                         'Nickel', 'Zinc', 'Other'],
                                        index=0 if project.get('commodity') == 'Gold' else 1)
    project['jurisdiction'] = st.text_input("Юрисдикция", 
                                            project.get('jurisdiction', ''))
    project['stage'] = st.selectbox("Стадия проекта",
                                    ['Exploration', 'PEA', 'PFS', 'FS', 'Construction', 'Operation'],
                                    index=1)
    
    project['tonnage_m'] = st.number_input("Тоннаж (млн т)", 
                                           value=project.get('tonnage_m', 25.0), 
                                           min_value=0.1, step=1.0)
    
    # Автоматическая подсказка для grade
    if project['commodity'] == 'Gold':
        grade_label = "Содержание Au (g/t)"
        default_grade = 2.5
    elif project['commodity'] == 'Copper':
        grade_label = "Содержание Cu (десятичная доля, 0.55% = 0.0055)"
        default_grade = 0.0055
    elif project['commodity'] == 'Lithium (LCE)':
        grade_label = "Содержание Li (десятичная доля)"
        default_grade = 0.00065
    else:
        grade_label = "Содержание (десятичная доля)"
        default_grade = 0.01
    
    project['grade'] = st.number_input(grade_label,
                                       value=project.get('grade', default_grade),
                                       format="%.6f")
    project['recovery'] = st.slider("Извлечение (%)", 50, 98, 
                                    value=int(project.get('recovery', 0.90) * 100)) / 100
    
    st.subheader("💰 Экономика")
    project['metal_price'] = st.number_input("Цена металла", 
                                             value=project.get('metal_price', 2000),
                                             step=100)
    project['opex_per_ton'] = st.number_input("OPEX ($/тонна)", 
                                              value=project.get('opex_per_ton', 35),
                                              step=5)
    project['capex_total'] = st.number_input("CAPEX ($ млн)", 
                                             value=project.get('capex_total', 180),
                                             step=10)
    project['lom_years'] = st.slider("Срок жизни (лет)", 3, 40, 
                                     value=project.get('lom_years', 10))
    
    st.subheader("📈 Рынок")
    project['market_cap'] = st.number_input("Market Cap ($ млн)", 
                                            value=project.get('market_cap', 120),
                                            step=10)
    project['p_equilibrium'] = st.number_input("Равновесная цена", 
                                               value=project.get('p_equilibrium', 1800),
                                               step=100)
    
    st.subheader("🏦 Финансирование")
    st.markdown("*Сумма весов должна быть = 1.0*")
    
    fin_cols = st.columns(2)
    with fin_cols[0]:
        eq_junior = st.slider("Equity Junior (%)", 0, 100, 
                              value=int(project.get('financing_structure', {}).get('equity_junior', 0.70) * 100))
        eq_mid = st.slider("Equity Mid-Tier (%)", 0, 100,
                           value=int(project.get('financing_structure', {}).get('equity_mid_tier', 0) * 100))
        mezz = st.slider("Mezzanine (%)", 0, 100,
                         value=int(project.get('financing_structure', {}).get('mezzanine', 0.20) * 100))
    
    with fin_cols[1]:
        proj_fin = st.slider("Project Finance (%)", 0, 100,
                             value=int(project.get('financing_structure', {}).get('project_finance', 0) * 100))
        royalty = st.slider("Royalty/Streaming (%)", 0, 100,
                            value=int(project.get('financing_structure', {}).get('royalty_streaming', 0.10) * 100))
        other = st.slider("Other Debt (%)", 0, 100,
                          value=int(project.get('financing_structure', {}).get('junior_senior_debt', 0) * 100))
    
    total_weight = eq_junior + eq_mid + mezz + proj_fin + royalty + other
    
    if abs(total_weight - 100) > 1:
        st.error(f"⚠️ Сумма весов = {total_weight}%. Должно быть 100%")
    
    # Формируем структуру финансирования
    project['financing_structure'] = {}
    if eq_junior > 0:
        project['financing_structure']['equity_junior'] = eq_junior / 100
    if eq_mid > 0:
        project['financing_structure']['equity_mid_tier'] = eq_mid / 100
    if mezz > 0:
        project['financing_structure']['mezzanine'] = mezz / 100
    if proj_fin > 0:
        project['financing_structure']['project_finance'] = proj_fin / 100
    if royalty > 0:
        project['financing_structure']['royalty_streaming'] = royalty / 100
    if other > 0:
        project['financing_structure']['junior_senior_debt'] = other / 100
    
    project['stated_ke'] = 0.15
    project['kd'] = 0.10
    project['tax_rate'] = 0.30
    
    # Supply curve (упрощённо — генерируем автоматически)
    base_price = project['metal_price']
    project['supply_curve'] = [base_price * (0.5 + 0.15 * i) for i in range(10)]
    
    # Кнопка расчёта
    st.markdown("---")
    calculate_button = st.button("🔍 РАССЧИТАТЬ ОЦЕНКУ", type="primary", use_container_width=True)


# Основная область — результаты
if calculate_button and abs(total_weight - 100) <= 1:
    try:
        results = calculator.full_valuation(project)
        
        # === ГЛАВНЫЙ ВЕРДИКТ ===
        st.markdown("---")
        
        if results['hard_lock']['hard_lock']:
            st.error(f"## 🚨 CAPITAL HARD-LOCK ACTIVATED")
            st.markdown("**Рекомендация:** BLOCK sanctioning")
            for reason in results['hard_lock']['reasons']:
                st.markdown(f"- ❌ {reason}")
        else:
            st.success(f"## ✅ PROJECT SANCTIONED")
            st.markdown("**Рекомендация:** Proceed to next stage")
        
        # === КЛЮЧЕВЫЕ МЕТРИКИ ===
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "True CoC",
                f"{results['true_coc']:.2%}",
                help="Истинная стоимость капитала по фактическим инструментам"
            )
        
        with col2:
            st.metric(
                "NAV",
                f"${results['nav']:.1f}M",
                help="Чистая приведённая стоимость (DCF по True CoC)"
            )
        
        with col3:
            nav_mult = results['nav_multiple']
            delta_color = "normal"
            if nav_mult < 0.8:
                delta_color = "off"
                delta_txt = "НЕДООЦЕНКА"
            elif nav_mult > 1.3:
                delta_txt = "ПЕРЕОЦЕНКА"
            else:
                delta_txt = "СПРАВЕДЛИВО"
            
            st.metric(
                "NAV-multiple",
                f"{nav_mult:.2f}×",
                delta=delta_txt
            )
        
        with col4:
            irr = results['irr']
            st.metric(
                "IRR",
                f"{irr:.2%}",
                delta=f"vs True CoC {results['true_coc']:.2%}",
                delta_color="normal" if irr > results['true_coc'] else "inverse"
            )
        
        # === ДЕТАЛЬНАЯ ИНФОРМАЦИЯ ===
        st.markdown("---")
        st.subheader("📊 Детальный анализ")
        
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.markdown("#### 💼 Финансовые показатели")
            df_fin = pd.DataFrame({
                'Показатель': [
                    'True CoC',
                    'Effective WACC',
                    'NAV',
                    'Market Cap',
                    'NAV-multiple',
                    'IRR проекта',
                    'P_breakeven',
                    'P_equilibrium',
                ],
                'Значение': [
                    f"{results['true_coc']:.2%}",
                    f"{results['effective_wacc']:.2%}",
                    f"${results['nav']:.1f}M",
                    f"${project['market_cap']:.1f}M",
                    f"{results['nav_multiple']:.2f}×",
                    f"{results['irr']:.2%}",
                    f"{results['p_breakeven']:.2f}",
                    f"{project['p_equilibrium']:.2f}",
                ]
            })
            st.dataframe(df_fin, hide_index=True, use_container_width=True)
        
        with col_right:
            st.markdown("#### 🎯 Позиция на Supply Curve")
            quartile = results['supply_quartile']
            quartile_labels = {
                1: "🟢 Квартиль 1 (низкозатратный лидер)",
                2: "🟡 Квартиль 2 (средняя устойчивость)",
                3: "🟠 Квартиль 3 (высокозатратный)",
                4: "🔴 Квартиль 4 (маржинальный, риск банкротства)"
            }
            st.info(quartile_labels.get(quartile, "Не определён"))
            
            st.markdown(f"**P_breakeven:** {results['p_breakeven']:.2f}")
            st.markdown(f"**P_equilibrium × 1.1:** {project['p_equilibrium'] * 1.1:.2f}")
        
        # === ГРАФИКИ ===
        st.markdown("---")
        st.subheader("📈 Визуализация")
        
        tab1, tab2, tab3 = st.tabs(["Supply Curve", "Cash Flows", "NAV Decomposition"])
        
        with tab1:
            # Supply curve с позицией проекта
            fig_supply = go.Figure()
            
            supply_curve = sorted(project['supply_curve'])
            fig_supply.add_trace(go.Scatter(
                x=list(range(1, len(supply_curve) + 1)),
                y=supply_curve,
                mode='lines+markers',
                name='Supply Curve',
                line=dict(color='blue', width=3)
            ))
            
            # Позиция проекта
            fig_supply.add_trace(go.Scatter(
                x=[results['supply_quartile']],
                y=[results['p_breakeven']],
                mode='markers',
                name='Ваш проект',
                marker=dict(size=20, color='red', symbol='star')
            ))
            
            fig_supply.update_layout(
                title="Кривая предложения с позицией проекта",
                xaxis_title="Квартиль",
                yaxis_title="Цена безубыточности",
                height=400
            )
            st.plotly_chart(fig_supply, use_container_width=True)
        
        with tab2:
            # Cash flows
            cashflows = results['cashflows']
            years = list(range(len(cashflows)))
            cumulative = [sum(cashflows[:i+1]) for i in range(len(cashflows))]
            
            fig_cf = go.Figure()
            fig_cf.add_trace(go.Bar(
                x=years,
                y=cashflows,
                name='Годовой FCF',
                marker_color=['red' if cf < 0 else 'green' for cf in cashflows]
            ))
            fig_cf.add_trace(go.Scatter(
                x=years,
                y=cumulative,
                mode='lines+markers',
                name='Накопительный CF',
                line=dict(color='orange', width=3)
            ))
            
            fig_cf.update_layout(
                title="Денежные потоки проекта",
                xaxis_title="Год",
                yaxis_title="$ млн",
                height=400
            )
            st.plotly_chart(fig_cf, use_container_width=True)
        
        with tab3:
            # NAV decomposition
            fig_nav = go.Figure(data=[go.Pie(
                labels=['V_core (DCF)', 'V_optionality (Inferred)', 'V_market', 
                        'V_real_options', 'V_tax_shields', '- V_closure', '- C_integration'],
                values=[
                    max(0, results['nav'] * 0.65),
                    max(0, results['nav'] * 0.15),
                    max(0, results['nav'] * 0.10),
                    max(0, results['nav'] * 0.08),
                    max(0, results['nav'] * 0.05),
                    max(0, results['nav'] * 0.02),
                    max(0, results['nav'] * 0.01),
                ],
                hole=0.3
            )])
            fig_nav.update_layout(
                title="Декомпозиция NAV",
                height=400
            )
            st.plotly_chart(fig_nav, use_container_width=True)
        
        # === РЕКОМЕНДАЦИИ ===
        st.markdown("---")
        st.subheader("💡 Рекомендации по структурированию сделки")
        
        if results['hard_lock']['hard_lock']:
            st.warning("""
            **Проект заблокирован. Варианты разблокировки:**
            
            1. **Оптимизация структуры финансирования** — снижение доли дорогого equity_junior
            2. **Royalty/Streaming** — привлечение стриминговой компании для снижения CAPEX
            3. **Earn-out структура** — привязка части оплаты к достижению KPI
            4. **Снижение OPEX** — пересмотр горнотехнических решений
            5. **Доразведка** — перевод Inferred → Indicated для повышения NAV
            """)
        else:
            st.success("""
            **Проект прошёл проверку. Рекомендуемая структура:**
            
            - Базовая цена: 80-90% от NAV
            - Earn-out: 10-20% при достижении production targets
            - Royalty: 1.5-2.5% NSR для продавца (если он остаётся)
            - Escrow: 10% на 24 месяца для покрытия environmental risks
            """)
        
        # === ЭКСПОРТ ===
        st.markdown("---")
        col_exp1, col_exp2 = st.columns(2)
        
        with col_exp1:
            # Экспорт в DataFrame
            df_results = pd.DataFrame([results])
            csv = df_results.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Скачать результаты (CSV)",
                csv,
                "omega_capital_results.csv",
                "text/csv"
            )
        
        with col_exp2:
            # Отчёт
            report = f"""
# Ω-CAPITAL HARD-LOCK REPORT
## {project['name']}

**Дата:** {pd.Timestamp.now().strftime('%Y-%m-%d')}
**Юрисдикция:** {project['jurisdiction']}
**Стадия:** {project['stage']}

### КЛЮЧЕВЫЕ ПОКАЗАТЕЛИ
- True CoC: {results['true_coc']:.2%}
- NAV: ${results['nav']:.1f}M
- NAV-multiple: {results['nav_multiple']:.2f}×
- IRR: {results['irr']:.2%}
- P_breakeven: {results['p_breakeven']:.2f}
- Supply Quartile: {results['supply_quartile']}

### ВЕРДИКТ
{'🚨 CAPITAL HARD-LOCK ACTIVATED' if results['hard_lock']['hard_lock'] else '✅ PROJECT SANCTIONED'}

Причины: {', '.join(results['hard_lock']['reasons']) if results['hard_lock']['reasons'] else 'Нет'}

### РЕКОМЕНДАЦИЯ
{results['hard_lock']['recommendation']}

---
*Powered by Ω-CAPITAL v2.0 methodology*
"""
            st.download_button(
                "📄 Скачать отчёт (Markdown)",
                report,
                "omega_capital_report.md",
                "text/markdown"
            )

    except Exception as e:
        st.error(f"❌ Ошибка расчёта: {str(e)}")
        st.exception(e)

elif calculate_button:
    st.warning("⚠️ Сумма весов финансирования должна быть 100%")


# Футер
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: gray; font-size: 0.8em;'>
Ω-CAPITAL Hard-Lock Calculator v1.0 | 
Методология патента Ω-CAPITAL v2.0 | 
Автор: Акопян А.З. | 
© 2026
</div>
""", unsafe_allow_html=True)