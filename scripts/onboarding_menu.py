#!/usr/bin/env python3
"""
Onboarding & Menu Comercial Interativo — Antigravity Turbinado
Simulador e interface CLI para escolha de pacotes comerciais com suporte a menu voltar.
"""

import sys

def clear_screen():
    print("\n" * 2)

def menu_principal():
    while True:
        clear_screen()
        print("=" * 65)
        print("🚀 BEM-VINDO AO ANTIGRAVITY TURBINADO — MENU COMERCIAL OFICIAL")
        print("Canal Oficial Telegram: @xprotorkzdev | Gateway: Sharkbot")
        print("=" * 65)
        print("1. Conhecer os Recursos do Kit")
        print("2. Escolher Plano / Fazer Upgrade")
        print("3. Validar Ambiente Local (Doctor)")
        print("4. Falar com Engenheiro no Telegram (@xprotorkzdev)")
        print("0. Sair")
        print("=" * 65)
        
        escolha = input("Selecione uma opção [0-4]: ").strip()
        
        if escolha == "1":
            menu_recursos()
        elif escolha == "2":
            menu_planos()
        elif escolha == "3":
            import subprocess
            subprocess.run([sys.executable, "scripts/doctor.py"])
            input("\nPressione ENTER para voltar ao menu...")
        elif escolha == "4":
            print("\n👉 Acesse diretamente: https://t.me/xprotorkzdev")
            input("Pressione ENTER para voltar ao menu...")
        elif escolha == "0":
            print("\nEncerrando. Obrigado por utilizar o Antigravity Turbinado!")
            break
        else:
            print("\nOpção inválida. Tente novamente.")

def menu_recursos():
    clear_screen()
    print("=" * 65)
    print("📌 RECURSOS PRINCIPAIS DO ANTIGRAVITY TURBINADO")
    print("=" * 65)
    print("• ChatGPT como Planner Oficial (Custom Instructions inclusas)")
    print("• GitHub como Fonte Única de Verdade (Issues estruturadas v5)")
    print("• Antigravity como Único Executor Local (Modo autônomo total no workspace)")
    print("• Sentinela Guardião Transversal (Scope Lock e Zero Segredos)")
    print("• 100 Skills Nativas Essenciais + Roteador para 2.488 skills")
    print("• Suporte Completo macOS e Windows com instaladores inteligentes")
    print("=" * 65)
    input("\nPressione ENTER para voltar ao menu principal...")

def menu_planos():
    while True:
        clear_screen()
        print("=" * 65)
        print("💎 ESCOLHA SEU PLANO DE ACESSO")
        print("=" * 65)
        print("[1] PLANO CORE — R$ 299,00")
        print("    • Instalação Completa do Antigravity Turbinado")
        print("    • Sentinela Guardião v2.0 + Scope Lock permanente")
        print("    • 100 Skills Nativas + Skill Router com acervo de 2.488 skills")
        print("    • Templates de Governança e Perfil do ChatGPT Planner")
        print()
        print("[2] COMBO PRO (COM GEMINI 18 MESES) — R$ 399,00 (RECOMENDADO)")
        print("    • Tudo do Plano Core")
        print("    • CONTA GOOGLE GEMINI PRO/ULTRA CONFIGURADA POR 18 MESES")
        print("    • Suporte Prioritário Direto com Engenharia via @xprotorkzdev")
        print("    • Onboarding Guiado One-on-One do seu Primeiro Projeto")
        print()
        print("[0] ⬅️ Voltar ao Menu Principal")
        print("=" * 65)
        
        escolha = input("Selecione uma opção [0-2]: ").strip()
        
        if escolha == "1":
            checkout_plano("Plano Core", 299)
        elif escolha == "2":
            checkout_plano("Combo Pro (Com Gemini 18 Meses)", 399)
        elif escolha == "0":
            break
        else:
            print("\nOpção inválida. Tente novamente.")

def checkout_plano(nome_plano, valor):
    clear_screen()
    print("=" * 65)
    print(f"🛒 FINALIZAR PEDIDO: {nome_plano.upper()} — R$ {valor},00")
    print("=" * 65)
    print("Para efetuar o pagamento via Sharkbot e receber a liberação imediata:")
    print("1. Envie uma mensagem para nosso bot no Telegram: @xprotorkzdev")
    print(f"2. Digite ou clique na opção: 'COMPRAR {nome_plano}'")
    print("3. O pagamento Pix com aprovação instantânea será gerado na hora.")
    print("4. Sua chave e acesso ao repositório privado serão liberados automaticamente.")
    print("=" * 65)
    input("\nPressione ENTER para voltar à lista de planos...")

if __name__ == "__main__":
    menu_principal()
