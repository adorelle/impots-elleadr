import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO
from datetime import datetime

st.set_page_config(
    page_title="Calculateur d'Impôt Progressif",
    page_icon="💰",
    layout="wide"
)

TAX_BRACKETS_BY_YEAR = {
    "2025": [
        {"min": 0, "max": 10064, "rate": 0.00},
        {"min": 10064, "max": 25659, "rate": 0.11},
        {"min": 25659, "max": 73369, "rate": 0.30},
        {"min": 73369, "max": 157806, "rate": 0.41},
        {"min": 157806, "max": float('inf'), "rate": 0.45},
    ],
    "2024": [
        {"min": 0, "max": 9875, "rate": 0.00},
        {"min": 9875, "max": 25175, "rate": 0.10},
        {"min": 25175, "max": 72000, "rate": 0.28},
        {"min": 72000, "max": 155000, "rate": 0.40},
        {"min": 155000, "max": float('inf'), "rate": 0.44},
    ],
    "2023": [
        {"min": 0, "max": 9325, "rate": 0.00},
        {"min": 9325, "max": 24500, "rate": 0.10},
        {"min": 24500, "max": 70500, "rate": 0.27},
        {"min": 70500, "max": 152000, "rate": 0.39},
        {"min": 152000, "max": float('inf'), "rate": 0.43},
    ],
    "2022": [
        {"min": 0, "max": 8900, "rate": 0.00},
        {"min": 8900, "max": 23850, "rate": 0.09},
        {"min": 23850, "max": 68500, "rate": 0.26},
        {"min": 68500, "max": 148000, "rate": 0.38},
        {"min": 148000, "max": float('inf'), "rate": 0.42},
    ],
}

def calculate_tax(income, year="2025"):
    """Calculate progressive tax based on income brackets for a given year"""
    brackets = TAX_BRACKETS_BY_YEAR.get(year, TAX_BRACKETS_BY_YEAR["2025"])

    total_tax = 0
    for i, bracket in enumerate(brackets):
        if income > bracket["min"]:
            taxable_in_bracket = min(income, bracket["max"]) - bracket["min"]
            tax_in_bracket = taxable_in_bracket * bracket["rate"]
            total_tax += tax_in_bracket

    return total_tax

def get_bracket_breakdown(income, year="2025"):
    """Get detailed breakdown of tax per bracket for a given year"""
    brackets = TAX_BRACKETS_BY_YEAR.get(year, TAX_BRACKETS_BY_YEAR["2025"])

    breakdown = []
    for bracket in brackets:
        if income > bracket["min"]:
            max_val = bracket["max"] if bracket["max"] != float('inf') else income
            taxable_in_bracket = min(income, bracket["max"]) - bracket["min"]
            tax_in_bracket = taxable_in_bracket * bracket["rate"]

            if bracket["max"] == float('inf'):
                bracket_name = f"{bracket['min']:,.0f} $ +"
            else:
                bracket_name = f"{bracket['min']:,.0f} $ - {bracket['max']:,.0f} $"

            breakdown.append({
                "Tranche": bracket_name,
                "Taux": f"{bracket['rate']*100:.0f}%",
                "Revenu Imposable": f"{taxable_in_bracket:,.2f} $",
                "Montant d'Impôt": f"{tax_in_bracket:,.2f} $",
                "tax_amount_raw": tax_in_bracket
            })

    return breakdown

def generate_pdf_report(income, deductions, credits, taxable_income, total_tax, effective_rate, net_income, breakdown):
    """Generate a PDF tax summary report"""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#FF6B9D'),
        spaceAfter=30,
        alignment=1
    )

    story.append(Paragraph("Rapport d'Impôt sur le Revenu", title_style))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d/%m/%Y à %H:%M')}", styles['Normal']))
    story.append(Spacer(1, 0.3*inch))

    summary_data = [
        ['Métrique', 'Valeur'],
        ['Revenu Brut', f"{income:,.2f} $"],
        ['Déductions Totales', f"{deductions:,.2f} $"],
        ['Crédits d\'Impôt', f"{credits:,.2f} $"],
        ['Revenu Imposable', f"{taxable_income:,.2f} $"],
        ['Impôt Total Dû', f"{total_tax:,.2f} $"],
        ['Taux d\'Imposition Effectif', f"{effective_rate:.2f}%"],
        ['Revenu Net', f"{net_income:,.2f} $"],
    ]

    summary_table = Table(summary_data, colWidths=[3*inch, 2*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#FF6B9D')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 11),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFF0F5'), colors.lightgrey]),
    ]))

    story.append(summary_table)
    story.append(Spacer(1, 0.5*inch))

    story.append(Paragraph("Détails par Tranche d'Impôt", styles['Heading2']))
    story.append(Spacer(1, 0.2*inch))

    bracket_data = [['Tranche', 'Taux', 'Revenu Imposable', 'Montant d\'Impôt']]
    for item in breakdown:
        bracket_data.append([
            item['Tranche'],
            item['Taux'],
            item['Revenu Imposable'],
            item['Montant d\'Impôt']
        ])

    bracket_table = Table(bracket_data, colWidths=[1.5*inch, 1*inch, 1.75*inch, 1.75*inch])
    bracket_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#87CEEB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#FFF0F5'), colors.lightgrey]),
    ]))

    story.append(bracket_table)
    story.append(Spacer(1, 0.5*inch))

    story.append(Paragraph("Note: Les taux d'imposition progressifs s'appliquent au revenu dans des plages spécifiques. Vous ne payez le taux plus élevé que sur le revenu au-dessus de chaque seuil.", styles['Italic']))

    doc.build(story)
    buffer.seek(0)
    return buffer

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #FFE4E1 0%, #FFEFD5 50%, #E0F8F7 100%);
    }
    .stTitle {
        color: #FF6B9D !important;
        text-align: center;
        font-size: 3rem !important;
        text-shadow: 2px 2px 4px rgba(255, 107, 157, 0.3);
    }
    .stMarkdown h2, .stMarkdown h3 {
        color: #FF6B9D !important;
    }
    div[data-testid="stMetricValue"] {
        color: #E65C8F !important;
        font-weight: 600;
    }
    div[data-testid="stMetricLabel"] {
        color: #2D5A5A !important;
        font-weight: 500;
    }
    .stDataFrame {
        background-color: rgba(255, 255, 255, 0.9);
        border-radius: 10px;
        padding: 10px;
    }
</style>
""", unsafe_allow_html=True)

st.title("💰 Calculateur d'Impôt Progressif")
st.markdown("<p style='text-align: center; color: #2D5A5A; font-size: 1.1em;'>✨ Calculez votre impôt en fonction des tranches progressives ✨</p>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["📊 Calcul Simple", "⚖️ Mode Comparaison", "📅 Comparaison Historique"])

with tab1:

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("📋 Informations sur le Revenu")

        income = st.number_input(
            "Entrez Votre Revenu Annuel ($)",
            min_value=0,
            max_value=10000000,
            value=50000,
            step=1000,
            format="%d"
        )

        st.markdown("---")
        st.subheader("🎯 Déductions et Crédits")

        with st.expander("Ajouter des Déductions", expanded=False):
            deduction_401k = st.number_input(
                "Cotisations 401(k)/REER ($)",
                min_value=0,
                max_value=100000,
                value=0,
                step=500,
                help="Cotisations à un régime de retraite"
            )

            deduction_medical = st.number_input(
                "Frais Médicaux ($)",
                min_value=0,
                max_value=100000,
                value=0,
                step=100,
                help="Dépenses médicales admissibles"
            )

            deduction_charitable = st.number_input(
                "Dons de Charité ($)",
                min_value=0,
                max_value=100000,
                value=0,
                step=100,
                help="Dons à des organismes de bienfaisance"
            )

            deduction_mortgage = st.number_input(
                "Intérêts Hypothécaires ($)",
                min_value=0,
                max_value=100000,
                value=0,
                step=500,
                help="Intérêts payés sur prêt hypothécaire"
            )

        with st.expander("Ajouter des Crédits d'Impôt", expanded=False):
            credit_child = st.number_input(
                "Crédit pour Enfants ($)",
                min_value=0,
                max_value=50000,
                value=0,
                step=500,
                help="Crédit d'impôt pour enfants à charge"
            )

            credit_education = st.number_input(
                "Crédit Éducation ($)",
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                help="Crédits pour frais de scolarité"
            )

            credit_energy = st.number_input(
                "Crédit Énergie Verte ($)",
                min_value=0,
                max_value=50000,
                value=0,
                step=100,
                help="Crédit pour améliorations écoénergétiques"
            )

        total_deductions = deduction_401k + deduction_medical + deduction_charitable + deduction_mortgage
        total_credits = credit_child + credit_education + credit_energy

        st.markdown("---")

        if income > 0:
            taxable_income = max(0, income - total_deductions)

            gross_tax = calculate_tax(taxable_income)

            total_tax = max(0, gross_tax - total_credits)

            effective_rate = (total_tax / income * 100) if income > 0 else 0
            net_income = income - total_tax

            st.subheader("📊 Résumé")

            if total_deductions > 0 or total_credits > 0:
                st.info(f"💡 Déductions: {total_deductions:,.2f} $ | Crédits: {total_credits:,.2f} $")

            metric_col1, metric_col2 = st.columns(2)
            with metric_col1:
                st.metric("Impôt Total Dû", f"{total_tax:,.2f} $")
                st.metric("Revenu Net", f"{net_income:,.2f} $")

            with metric_col2:
                st.metric("Taux d'Imposition Effectif", f"{effective_rate:.2f}%")
                st.metric("Revenu Brut", f"{income:,.2f} $")

            if total_deductions > 0:
                st.metric("Revenu Imposable", f"{taxable_income:,.2f} $")

            st.markdown("---")

            breakdown = get_bracket_breakdown(taxable_income)
            pdf_buffer = generate_pdf_report(
                income,
                total_deductions,
                total_credits,
                taxable_income,
                total_tax,
                effective_rate,
                net_income,
                breakdown
            )

            st.download_button(
                label="📄 Télécharger le Rapport PDF",
                data=pdf_buffer,
                file_name=f"rapport_impot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )

    with col2:
        if income > 0:
            st.subheader("🌸 Visualisation des Tranches d'Impôt")

            taxable_income = max(0, income - total_deductions)
            breakdown = get_bracket_breakdown(taxable_income)

            if breakdown:
                labels = [b["Tranche"] for b in breakdown]
                values = [b["tax_amount_raw"] for b in breakdown]

                colors = ['#FFB6C1', '#FFD700', '#87CEEB', '#98FB98', '#FFA07A']

                fig = go.Figure(data=[go.Pie(
                    labels=labels,
                    values=values,
                    hole=.4,
                    marker=dict(colors=colors[:len(labels)]),
                    textposition='auto',
                    textinfo='label+percent',
                    hovertemplate='<b>%{label}</b><br>Impôt: %{value:,.2f} $<br>%{percent}<extra></extra>'
                )])

                fig.update_layout(
                    showlegend=True,
                    height=400,
                    margin=dict(t=20, b=20, l=20, r=20),
                    legend=dict(
                        orientation="v",
                        yanchor="middle",
                        y=0.5,
                        xanchor="left",
                        x=1.05,
                        font=dict(color='#2D5A5A')
                    ),
                    paper_bgcolor='rgba(255,255,255,0.3)',
                    plot_bgcolor='rgba(255,255,255,0.3)'
                )

                st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")

    if income > 0:
        st.subheader("📝 Détails par Tranche")

        taxable_income = max(0, income - total_deductions)
        breakdown = get_bracket_breakdown(taxable_income)

        if breakdown:
            df = pd.DataFrame(breakdown)
            df = df.drop('tax_amount_raw', axis=1)

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

            st.markdown("---")

            st.subheader("🎨 Répartition du Revenu par Tranche")

            brackets_2025 = TAX_BRACKETS_BY_YEAR["2025"]
            bracket_ranges = []
            for bracket in brackets_2025:
                if bracket["max"] == float('inf'):
                    bracket_ranges.append({
                        "name": f"{bracket['min']:,.0f} $ +",
                        "min": bracket["min"],
                        "max": max(taxable_income + 1000, bracket["min"] + 10000)
                    })
                else:
                    bracket_ranges.append({
                        "name": f"{bracket['min']:,.0f} $ - {bracket['max']:,.0f} $",
                        "min": bracket["min"],
                        "max": bracket["max"]
                    })

            bracket_names = []
            income_in_bracket = []
            colors_bar = []

            color_palette = ['#FFB6C1', '#FFD700', '#87CEEB', '#98FB98', '#FFA07A']

            for idx, bracket in enumerate(bracket_ranges):
                bracket_names.append(bracket["name"])
                if taxable_income > bracket["min"]:
                    amount = min(taxable_income, bracket["max"]) - bracket["min"]
                    income_in_bracket.append(amount)
                    colors_bar.append(color_palette[idx])
                else:
                    income_in_bracket.append(0)
                    colors_bar.append('#F5E6FF')

            fig2 = go.Figure(data=[
                go.Bar(
                    x=bracket_names,
                    y=income_in_bracket,
                    marker=dict(color=colors_bar),
                    text=[f"{val:,.0f} $" if val > 0 else "" for val in income_in_bracket],
                    textposition='auto',
                    hovertemplate='<b>%{x}</b><br>Revenu dans la tranche: %{y:,.2f} $<extra></extra>'
                )
            ])

            fig2.update_layout(
                xaxis_title="Tranche d'Impôt",
                yaxis_title="Montant du Revenu ($)",
                height=400,
                showlegend=False,
                margin=dict(t=20, b=100, l=20, r=20),
                xaxis=dict(tickangle=-45, tickfont=dict(color='#2D5A5A')),
                yaxis=dict(tickfont=dict(color='#2D5A5A')),
                paper_bgcolor='rgba(255,255,255,0.3)',
                plot_bgcolor='rgba(255,255,255,0.3)'
            )

            st.plotly_chart(fig2, use_container_width=True)

with tab2:
    st.subheader("⚖️ Mode Comparaison")
    st.markdown("Comparez les calculs d'impôt pour différents niveaux de revenu côte à côte")

    num_scenarios = st.radio(
        "Nombre de scénarios à comparer:",
        options=[2, 3],
        horizontal=True
    )

    st.markdown("---")

    cols = st.columns(num_scenarios)

    scenarios = []

    for i, col in enumerate(cols):
        with col:
            st.markdown(f"### 📊 Scénario {i+1}")

            scenario_income = st.number_input(
                f"Revenu Annuel ($)",
                min_value=0,
                max_value=10000000,
                value=30000 + (i * 30000),
                step=1000,
                format="%d",
                key=f"income_{i}"
            )

            scenario_deductions = st.number_input(
                f"Déductions Totales ($)",
                min_value=0,
                max_value=100000,
                value=0,
                step=500,
                key=f"deductions_{i}"
            )

            scenario_credits = st.number_input(
                f"Crédits d'Impôt ($)",
                min_value=0,
                max_value=50000,
                value=0,
                step=500,
                key=f"credits_{i}"
            )

            taxable = max(0, scenario_income - scenario_deductions)
            gross_tax = calculate_tax(taxable)
            total_tax = max(0, gross_tax - scenario_credits)
            effective_rate = (total_tax / scenario_income * 100) if scenario_income > 0 else 0
            net_income = scenario_income - total_tax

            scenarios.append({
                "income": scenario_income,
                "deductions": scenario_deductions,
                "credits": scenario_credits,
                "taxable_income": taxable,
                "tax_owed": total_tax,
                "effective_rate": effective_rate,
                "net_income": net_income
            })

            st.markdown("---")

            st.metric("Impôt Dû", f"{total_tax:,.2f} $")
            st.metric("Taux Effectif", f"{effective_rate:.2f}%")
            st.metric("Revenu Net", f"{net_income:,.2f} $")

    st.markdown("---")
    st.subheader("📊 Tableau Comparatif")

    comparison_data = {
        "Métrique": [
            "Revenu Brut",
            "Déductions",
            "Crédits",
            "Revenu Imposable",
            "Impôt Dû",
            "Taux Effectif",
            "Revenu Net"
        ]
    }

    for i, scenario in enumerate(scenarios):
        comparison_data[f"Scénario {i+1}"] = [
            f"{scenario['income']:,.2f} $",
            f"{scenario['deductions']:,.2f} $",
            f"{scenario['credits']:,.2f} $",
            f"{scenario['taxable_income']:,.2f} $",
            f"{scenario['tax_owed']:,.2f} $",
            f"{scenario['effective_rate']:.2f}%",
            f"{scenario['net_income']:,.2f} $"
        ]

    comparison_df = pd.DataFrame(comparison_data)

    st.dataframe(
        comparison_df,
        use_container_width=True,
        hide_index=True
    )

    st.markdown("---")
    st.subheader("📈 Visualisation Comparative")

    scenario_labels = [f"Scénario {i+1}" for i in range(num_scenarios)]
    tax_values = [s['tax_owed'] for s in scenarios]
    net_values = [s['net_income'] for s in scenarios]

    fig_comparison = go.Figure()

    fig_comparison.add_trace(go.Bar(
        name='Impôt Dû',
        x=scenario_labels,
        y=tax_values,
        marker_color='#FFA07A',
        text=[f"{val:,.0f} $" for val in tax_values],
        textposition='auto',
    ))

    fig_comparison.add_trace(go.Bar(
        name='Revenu Net',
        x=scenario_labels,
        y=net_values,
        marker_color='#98FB98',
        text=[f"{val:,.0f} $" for val in net_values],
        textposition='auto',
    ))

    fig_comparison.update_layout(
        barmode='group',
        xaxis_title="Scénarios",
        yaxis_title="Montant ($)",
        height=400,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(color='#2D5A5A')
        ),
        paper_bgcolor='rgba(255,255,255,0.3)',
        plot_bgcolor='rgba(255,255,255,0.3)',
        xaxis=dict(tickfont=dict(color='#2D5A5A')),
        yaxis=dict(tickfont=dict(color='#2D5A5A'))
    )

    st.plotly_chart(fig_comparison, use_container_width=True)

with tab3:
    st.subheader("📅 Comparaison Historique des Tranches d'Impôt")
    st.markdown("Comparez comment les taxes auraient changé pour le même revenu au fil des années")

    hist_col1, hist_col2 = st.columns([1, 2])

    with hist_col1:
        hist_income = st.number_input(
            "Revenu Annuel à Comparer ($)",
            min_value=0,
            max_value=10000000,
            value=75000,
            step=5000,
            format="%d",
            key="hist_income"
        )

        st.markdown("---")

        selected_years = st.multiselect(
            "Sélectionnez les Années à Comparer",
            options=["2022", "2023", "2024", "2025"],
            default=["2023", "2024", "2025"]
        )

    with hist_col2:
        if selected_years and hist_income > 0:
            year_comparisons = []

            for year in selected_years:
                tax = calculate_tax(hist_income, year)
                effective_rate = (tax / hist_income * 100) if hist_income > 0 else 0
                net_income = hist_income - tax

                year_comparisons.append({
                    "year": year,
                    "tax": tax,
                    "effective_rate": effective_rate,
                    "net_income": net_income
                })

            fig_hist = go.Figure()

            years = [y["year"] for y in year_comparisons]
            taxes = [y["tax"] for y in year_comparisons]
            rates = [y["effective_rate"] for y in year_comparisons]

            fig_hist.add_trace(go.Bar(
                x=years,
                y=taxes,
                name='Impôt Dû',
                marker_color='#FFA07A',
                text=[f"{val:,.0f} $" for val in taxes],
                textposition='auto',
                yaxis='y',
            ))

            fig_hist.add_trace(go.Scatter(
                x=years,
                y=rates,
                name='Taux Effectif (%)',
                marker=dict(color='#FF6B9D', size=10),
                line=dict(color='#FF6B9D', width=3),
                mode='lines+markers+text',
                text=[f"{val:.2f}%" for val in rates],
                textposition='top center',
                yaxis='y2'
            ))

            fig_hist.update_layout(
                title=f"Évolution de l'Impôt pour un Revenu de {hist_income:,.0f} $",
                xaxis=dict(title="Année", tickfont=dict(color='#2D5A5A')),
                yaxis=dict(
                    title=dict(text="Impôt Dû ($)", font=dict(color='#FFA07A')),
                    tickfont=dict(color='#2D5A5A')
                ),
                yaxis2=dict(
                    title=dict(text="Taux Effectif (%)", font=dict(color='#FF6B9D')),
                    tickfont=dict(color='#2D5A5A'),
                    overlaying='y',
                    side='right'
                ),
                height=400,
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1,
                    font=dict(color='#2D5A5A')
                ),
                paper_bgcolor='rgba(255,255,255,0.3)',
                plot_bgcolor='rgba(255,255,255,0.3)'
            )

            st.plotly_chart(fig_hist, use_container_width=True)

    if selected_years and hist_income > 0:
        st.markdown("---")
        st.subheader("📊 Tableau de Comparaison par Année")

        hist_data = {
            "Année": [],
            "Impôt Dû": [],
            "Taux Effectif": [],
            "Revenu Net": [],
            "Différence vs Année Précédente": []
        }

        sorted_years = sorted(selected_years)
        prev_tax = None

        for year in sorted_years:
            tax = calculate_tax(hist_income, year)
            effective_rate = (tax / hist_income * 100) if hist_income > 0 else 0
            net_income = hist_income - tax

            hist_data["Année"].append(year)
            hist_data["Impôt Dû"].append(f"{tax:,.2f} $")
            hist_data["Taux Effectif"].append(f"{effective_rate:.2f}%")
            hist_data["Revenu Net"].append(f"{net_income:,.2f} $")

            if prev_tax is not None:
                diff = tax - prev_tax
                diff_pct = (diff / prev_tax * 100) if prev_tax > 0 else 0
                hist_data["Différence vs Année Précédente"].append(
                    f"{diff:+,.2f} $ ({diff_pct:+.2f}%)"
                )
            else:
                hist_data["Différence vs Année Précédente"].append("N/A")

            prev_tax = tax

        hist_df = pd.DataFrame(hist_data)
        st.dataframe(hist_df, use_container_width=True, hide_index=True)

        st.markdown("---")
        st.subheader("📋 Détails des Tranches par Année")

        year_tabs = st.tabs(sorted_years)

        for i, year in enumerate(sorted_years):
            with year_tabs[i]:
                breakdown = get_bracket_breakdown(hist_income, year)
                if breakdown:
                    df_breakdown = pd.DataFrame(breakdown)
                    df_breakdown = df_breakdown.drop('tax_amount_raw', axis=1)
                    st.dataframe(df_breakdown, use_container_width=True, hide_index=True)

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #2D5A5A; font-size: 0.95em; background-color: rgba(255, 255, 255, 0.7); padding: 20px; border-radius: 15px;'>
    <p><strong>💡 Explication des Tranches d'Impôt:</strong></p>
    <p>Les taux d'imposition progressifs s'appliquent au revenu dans des plages spécifiques. Vous ne payez le taux plus élevé que sur le revenu au-dessus de chaque seuil.</p>
    <p style='font-size: 0.9em; margin-top: 10px;'>✨ Fait avec 💖 ✨</p>
    </div>
    """,
    unsafe_allow_html=True
)