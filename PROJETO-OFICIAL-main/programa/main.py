import os
from pathlib import Path
from logica import ArvoreWeb, GerenciadorBanco, RenderizadorPagina, LimiteFilhosError

class SimuladorNavegador:
    def __init__(self):
        self.__diretorio_base = Path(__file__).resolve().parent
        self.__banco = GerenciadorBanco(self.__diretorio_base)
        self.__renderizador = RenderizadorPagina(self.__banco.pasta_paginas)
        self.__historico = []
        self.__url_atual = ""
        self.__arvore = ArvoreWeb()
        self.__urls_cache = []

    def __sincronizar(self):
        self.__urls_cache = self.__banco.carregar_urls()
        self.__arvore = ArvoreWeb()
        for url in self.__urls_cache:
            try:
                self.__arvore.inserir(url)
                self.__renderizador.criar_pagina(url)
            except LimiteFilhosError:
                pass

    def __exibir_ui(self, links_disponiveis):
        os.system('cls' if os.name == 'nt' else 'clear')
        print("=" * 70)
        print(f" Historico de Acesso: {self.__historico if self.__historico else '[ Vazio ]'}")
        print(f" Home Atual: [{self.__url_atual if self.__url_atual else 'Navegando no Limbo'}]")
        print("=" * 70)
        print(" Links disponíveis:")
        if links_disponiveis:
            for link in links_disponiveis:
                print(f"   /{link}")
        else:
            print("   (Nenhum link disponivel. Você esta isoooolado.)")

        print("\n" + "-" * 23 + " RENDERIZAÇÃO DA PAGINA " + "-" * 23)
        if self.__url_atual:
            print(self.__renderizador.render(self.__url_atual))
        else:
            print("\n   [Navegador Inicializado] Digite um site como 'www.marciobomba.com'")
        print("-" * 70)
        print(" Comandos validos: #back | #showhist | #add <url> | #remover <url> | #reset | #help | #sair")
        print("-" * 70)

    def __cmd_help(self):
        print("""
-------------------------- MANUAL DO USUARIO DESESPERADO --------------------------
#sair          -> Desliga o simulador antes que de tela azul.
#back          -> Desempilha a ultima URL (Volta no tempo).
#showhist      -> Abre a caixa preta da pilha do seu historico.
#add <url>     -> Cria um novo site ou link (Maximo 2 filhos por pai, nao insista).
#remover <url> -> Deleta logicamente e manda o arquivo fisico pro espaco.
#reset         -> Zera o database e limpa todos os arquivos da pasta web_pages.
-----------------------------------------------------------------------------------""")
        input("\nPressione Enter para fechar o manual...")

    def __cmd_back(self):
     
        if self.__historico:
            self.__url_atual = self.__historico.pop()
            
        
        elif self.__url_atual != "":
            self.__url_atual = ""  
            
     
        else:
            print("\n[Aviso]: Voce ja esta na raiz do navegador (Home Inicial). Nao ha para onde voltar!")
            input("\nPressione Enter...")

    def __cmd_showhist(self):
        print("\n=== INVESTIGACAO DA ESTRUTURA ===")
        if self.__historico:
            for indice, url in enumerate(self.__historico, 1):
                print(f" -> Camada {indice}: [{url}]")
        else:
            print(" Nada na pilha. Limpissimo.")
        print("==========================================")
        input("\nPressione Enter...")

    def __cmd_add(self, texto_comando):
        nova_url = texto_comando.replace("#add ", "").strip()
        if not nova_url.startswith("/") and not nova_url.startswith(("www.", "http://", "https://")):
            print("\n[Erro de Sintaxe]: Isso nao parece uma URL. Tente algo com 'www.' ou '/'")
            input("\nPressione Enter...")
            return

        if nova_url in self.__urls_cache:
            print("\n[Erro]: Esse site ja existe no banco. Criatividade faltou!")
            input("\nPressione Enter...")
            return

        try:
            self.__arvore.inserir(nova_url)
            self.__renderizador.criar_pagina(nova_url)
            self.__banco.anexar_url(nova_url)
            print(f"\n[Sucesso]: '{nova_url}' foi adicionado e renderizado.")
        except LimiteFilhosError as e:
            print(f"\n[Erro de Estrutura de Dados]: {e}")
        except Exception as e:
            print(f"\n[Erro de Sistema]: {e}")
        input("\nPressione Enter...")

    def __cmd_remover(self, texto_comando):
        url_para_remover = texto_comando.replace("#remover ", "").strip()
        if url_para_remover not in self.__urls_cache:
            print(f"\n[Erro]: Nao da para remover o que nao existe: '{url_para_remover}'")
            input("\nPressione Enter...")
            return

        try:
            self.__urls_cache.remove(url_para_remover)
            self.__banco.salvar_urls(self.__urls_cache)
            self.__renderizador.deletar_pagina(url_para_remover)

            if self.__url_atual == url_para_remover:
                self.__url_atual = ""
            while url_para_remover in self.__historico:
                self.__historico.remove(url_para_remover)

            print(f"\n[Sucesso]: Site '{url_para_remover}' foi banido do sistema.")
        except Exception as e:
            print(f"\n[Erro ao Deletar]: {e}")
        input("\nPressione Enter...")

    def executar(self):
        while True:
            self.__sincronizar()
            links_disponiveis = self.__arvore.obter_links(self.__url_atual)
            self.__exibir_ui(links_disponiveis)
            
            entrada = input("url: ").strip()
            if not entrada:
                continue

            if entrada == "#sair":
                print("\nFechando abas... Adeus!")
                break
            elif entrada == "#help":
                self.__cmd_help()
                continue
            elif entrada == "#back":
                self.__cmd_back()
                continue
            elif entrada == "#showhist":
                self.__cmd_showhist()
                continue
            elif entrada == "#reset":
                confirmacao = input("Tem certeza que deseja resetar TUDO? (s/n): ").strip().lower()
                if confirmacao == 's':
                    self.__banco.limpar_tudo()
                    self.__url_atual = ""
                    self.__historico = []
                    print("\n[SUCESSO] Sistema totalmente resetado e limpo!")
                else:
                    print("\n[Operação Cancelada]")
                input("Pressione Enter...")
                continue
            elif entrada.startswith("#add "):
                self.__cmd_add(entrada)
                continue
            elif entrada.startswith("#remover "):
                self.__cmd_remover(entrada)
                continue

            destino = entrada
            if entrada.startswith("/"):
                sublink = entrada.replace("/", "", 1)
                if self.__url_atual:
                    if sublink in links_disponiveis:
                        destino = f"{self.__url_atual}/{sublink}"
                    else:
                        destino = f"{self.__url_atual}{entrada}"
                else:
                    destino = sublink

            if destino in self.__urls_cache:
                if self.__url_atual and self.__url_atual != destino:
                    self.__historico.append(self.__url_atual)
                self.__url_atual = destino
            else:
                print(f"\nErro 404: '{destino}' nao foi mapeado. Certeza que digitou certo?")
                input("Pressione Enter...")

if __name__ == "__main__":
    simulador = SimuladorNavegador()
    simulador.executar()