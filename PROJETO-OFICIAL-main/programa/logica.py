from pathlib import Path

class LimiteFilhosError(Exception):
    pass


class NoArv:
    def __init__(self, nome):
        self._nome = nome
        self._filhos = {}

    @property
    def nome(self):
        return self._nome

    @property
    def filhos(self):
        return self._filhos

    def tem_filho(self, nome):
        return nome in self._filhos

    def add_filho(self, nome):
       
        if nome not in self._filhos:
            self._filhos[nome] = NoArv(nome)
        return self._filhos[nome]

    def obter_filho(self, nome):
        return self._filhos.get(nome)


class ArvoreWeb:
    def __init__(self):
        self.__raiz = NoArv("raiz")

    def inserir(self, url):
        if not url:
            return
        partes = [p for p in url.split('/') if p]
        if not partes:
            return
        
        atual = self.__raiz
        for parte in partes:
          
            if atual != self.__raiz and len(atual.filhos) >= 2 and not atual.tem_filho(parte):
                raise LimiteFilhosError("Sem chance! Esta pagina interna ja atingiu o limite maximo de 2 sublinks.")
            atual = atual.add_filho(parte)

    def buscar(self, url_atual):
        if not url_atual:
            return self.__raiz
        partes = [p for p in url_atual.split('/') if p]
        
        atual = self.__raiz
        for parte in partes:
            if atual is None:
                return None
            atual = atual.obter_filho(parte)
        return atual

    def obter_links(self, url_atual):
        no = self.buscar(url_atual)
        if no and no.filhos:
            return list(no.filhos.keys())
        return []


class GerenciadorBanco:
    def __init__(self, diretorio_base: Path):
        self.__caminho_db = diretorio_base / 'database.txt'
        self.__pasta_paginas = diretorio_base / 'web_pages' 
        self.__inicializar_banco()

    @property
    def pasta_paginas(self):
        return self.__pasta_paginas

    def __inicializar_banco(self):
        if not self.__caminho_db.exists():
            urls_iniciais = [
                "www.marciobomba.com",
                "www.marciobomba.com/growth",
                "www.pablinho.dev",
                "www.pablinho.dev/gameplay"
            ]
            self.salvar_urls(urls_iniciais)

    def carregar_urls(self):
        if not self.__caminho_db.exists():
            return []
        with open(self.__caminho_db, 'r', encoding='utf-8') as f:
            return [linha.strip() for linha in f if linha.strip()]

    def salvar_urls(self, urls):
        with open(self.__caminho_db, 'w', encoding='utf-8') as f:
            for url in urls:
                f.write(f"{url}\n")

    def anexar_url(self, url):
        with open(self.__caminho_db, 'a', encoding='utf-8') as f:
            f.write(f"{url}\n")

    def limpar_tudo(self):
        """Deleta fisicamente todos os arquivos de páginas e limpa o banco de dados"""
        if self.__pasta_paginas.exists():
            for arquivo in self.__pasta_paginas.iterdir():
                if arquivo.is_file() and arquivo.suffix == '.txt':
                    arquivo.unlink()
        if self.__caminho_db.exists():
            self.__caminho_db.unlink()


class RenderizadorPagina:
    def __init__(self, pasta_paginas: Path):
        self.__pasta_paginas = pasta_paginas

    def __obter_nome_arquivo(self, url):
        nome = url.replace("/", "_").strip()
        if not nome.endswith(".txt"):
            return nome + ".txt"
        return nome

    def render(self, url):
        if not url:
            return ""
        nome_arquivo = self.__obter_nome_arquivo(url)
        caminho_completo = self.__pasta_paginas / nome_arquivo

        if caminho_completo.exists():
            with open(caminho_completo, "r", encoding="utf-8") as f:
                return f.read()
        
        if "faltou_feedback" in url:
            return "Erro 404: O feedback de Estrutura de Dados nao foi encontrado. Tente chorar no privado do Discord."
        if "marciobomba" in url:
            return "CUIDADO: ESTE SITE CONTERA UMA EXPLOSAO DE CONTEUDO EM 3... 2... 1..."
        if "pablinho" in url:
            return "Bem-vindo ao portal do Pablinho. 100% focado em commits na madrugada e codigos misteriosos."
            
        return f"Erro 404: O arquivo '{nome_arquivo}' sumiu do mapa. Rodou!"

    def criar_pagina(self, url):
        self.__pasta_paginas.mkdir(parents=True, exist_ok=True)
        nome_arquivo = self.__obter_nome_arquivo(url)
        caminho_completo = self.__pasta_paginas / nome_arquivo

        if not caminho_completo.exists():
            with open(caminho_completo, "w", encoding="utf-8") as f:
                f.write("======================================\n")
                f.write(f"       BEM-VINDO AO SITE: {url}\n")
                f.write("======================================\n")
                if "faltou_feedback" in url:
                    f.write("\n[Status: Esperando a nota ate agora...]")
                elif "marciobomba" in url:
                    f.write("\n[Status: Sistema altamente explosivo, afaste-se]")
                else:
                    f.write("\n[Esta pagina foi criada com sucesso pelo sistema]")

    def deletar_pagina(self, url):
        nome_arquivo = self.__obter_nome_arquivo(url)
        caminho_completo = self.__pasta_paginas / nome_arquivo
        if caminho_completo.exists():
            caminho_completo.unlink()