import os
import pathlib
import sys
import tempfile
import time
import urllib.request
from datetime import datetime
from getpass import getpass
from subprocess import DEVNULL, call
from selenium import webdriver

import requests
from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    TimeoutException, StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import Select, WebDriverWait

# Constantes
base_url = "http://servicos.jfpb.jus.br:8085/juntadas/backend/api"

url = "{0}/usuarios/login".format(base_url)
url_correspondencia = "{0}/correspondencia/".format(base_url)
url_relatorio_bot = "{0}/relatorio/".format(base_url)
url_relatorio_erro = "{0}/relatorio_erros/".format(base_url)

if getattr(sys, "frozen", False):
    GECKODRIVER_PATH = os.path.join(
        os.path.dirname(sys.executable), "geckodriver", "geckodriver.exe"
    )
else:
    GECKODRIVER_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)
                        ), "geckodriver", "geckodriver.exe"
    )

if getattr(sys, "frozen", False):
    AHK_PATH = os.path.join(
        os.path.dirname(sys.executable), "AutoHotkey", "AutoHotkey.exe"
    )
else:
    AHK_PATH = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "AutoHotkey",
        "AutoHotkey.exe",
    )


# Classes
class ErroBot(Exception):
    pass


# Funções utilitárias erros
def informar_erro(descricao_erro, numero_processo, token):
    headers = {"Token": token}
    descricao_erro = descricao_erro
    data_hora_texto = datetime.now().strftime("%d/%m/%Y %H:%M")
    relatorio = {
        "descricao": descricao_erro,
        "numero_processo": numero_processo,
        "data_hora": data_hora_texto,
    }
    requests.post(url=url_relatorio_erro, json=relatorio, headers=headers)


# Funções utilitárias selenium
def clicar_por_xpath(driver, elemento_xpath):
    for _ in range(10):
        try:
            driver.find_element_by_xpath(elemento_xpath).click()
            # deu certo
            return
        except (
            NoSuchElementException,
            ElementNotInteractableException,
            ElementClickInterceptedException,
        ):
            time.sleep(3.0)
    raise ErroBot(
        "Tempo limite decorrido sem que o elemento tenha sido encontrado.")


def clicar_por_id(driver, elemento_id):
    for _ in range(10):
        try:
            driver.find_element_by_id(elemento_id).click()
            # deu certo
            return
        except (
            NoSuchElementException,
            ElementNotInteractableException,
            ElementClickInterceptedException,
        ):
            time.sleep(2)
    raise ErroBot(
        "Tempo limite decorrido sem que o elemento tenha sido encontrado.")


def digitar_por_id(driver, elemento_id, texto):
    for _ in range(10):
        try:
            driver.find_element_by_id(elemento_id).clear()
            driver.find_element_by_id(elemento_id).send_keys(texto)
            # deu certo
            return
        except (
            NoSuchElementException,
            ElementNotInteractableException,
            ElementClickInterceptedException,
        ):
            time.sleep(2)
    raise ErroBot(
        "Tempo limite decorrido sem que o elemento tenha sido encontrado.")


def digitar_por_xpath(driver, elemento_xpath, texto):
    for _ in range(10):
        try:
            driver.find_element_by_xpath(elemento_xpath).clear()
            driver.find_element_by_xpath(elemento_xpath).send_keys(texto)
            # deu certo
            return
        except (
            NoSuchElementException,
            ElementNotInteractableException,
            ElementClickInterceptedException,
        ):
            time.sleep(2)
    raise ErroBot(
        "Tempo limite decorrido sem que o elemento tenha sido encontrado.")


def escolher_select_por_xpath(driver, elemento_xpath, texto_escolha):
    for _ in range(10):
        try:
            Select(driver.find_element_by_xpath(elemento_xpath)).select_by_visible_text(
                texto_escolha
            )
            return
        except (
            NoSuchElementException,
            ElementNotInteractableException,
            ElementClickInterceptedException,
        ):
            time.sleep(2)
    raise ErroBot(
        "Tempo limite decorrido sem que o elemento tenha sido encontrado.")


# Funções principais
def checar_se_backend_online():
    print("\nVerificando se o servidor está on-line ...")
    try:
        requests.get(url)
        print("O servidor escolhido está on-line.")
        return
    except ConnectionRefusedError:
        print(
            "\nErro: não foi possível efetuar a conexão com o servidor. Tente mais tarde ou contate o administrador."
        )
        quit()


def checar_credenciais_backend():
    for i in range(5):
        print("\nTentativa {}/5".format(i + 1))
        nome = input("Digite o nome do usuário ou '*sair': ")

        if nome == "*sair":
            print("### Até mais ###\n")
            quit()

        senha = getpass("Senha: ")
        user_data = {"username": nome, "senha": senha}

        print("\nIniciando a checagem do login e da senha...")
        response = requests.post(url=url, json=user_data)

        if response.status_code == 200:
            print("Login e senha conferidos com sucesso.")
            # deu certo
            usuario = response.json()
            status = response.status_code
            response_data = response.json()
            token = response_data["token"]
            return usuario, response_data, status, token
        else:
            # deu errado
            print(
                "Erro: usuário ou senha digitados incorretamente. Tente mais uma vez.\n"
            )


def obter_processos_aptos_juntada(response_data, token):
    print("\nIniciando a checagem dos processos aptos a juntada de ARs ...")
    headers = {"Token": token}
    request = requests.get(url_correspondencia, headers=headers)
    processos_data = request.json()
    processos = processos_data["correspondencia"]

    lista_processos = [
        {
            "id": processo["id"],
            "numProcesso": processo["numero_processo"],
            "destinatario": processo["destinatario"],
            "data": processo["data"],
            "status_bot": processo["status_bot"],
            "status": processo["status"],
            "anexo": processo["anexo"],
            "CUMPRIDO": processo["anexo"][0]["cumprido"],
        }
        for processo in processos
        if processo["status_bot"] == "Não houve tentativa"
        and processo["status"] != "Nao Upado"
    ]
    descricao = "Juntada de ARs"
    id_usuario = response_data["usuario"]["id"]
    numero_juntadas = len(lista_processos)
    atividade_bot_data = {
        "descricao": descricao,
        "usuario_id": id_usuario,
        "numero_juntadas": numero_juntadas,
    }

    atividade = requests.post(
        url=url_relatorio_bot, json=atividade_bot_data, headers=headers
    )
    id_relatorio = atividade.json()["relatorio"]["id"]

    print(
        "Foram encontrados {} processos aptos a juntada de AR.\n".format(
            len(lista_processos)
        )
    )
    return lista_processos, id_relatorio


def efetuar_download_pdfs(lista_processos, token):
    print("\r")
    print("Efetuando o download dos pdfs dos ARs ...")

    # criar diretorio dos ars
    ar_dir_path = "pdfs_ars/"
    if not os.path.exists(ar_dir_path):
        os.mkdir(ar_dir_path)

    for processo in lista_processos:
        # caminho arquivo
        caminho_arquivo = os.path.join(
            ar_dir_path, processo["numProcesso"]) + ".pdf"

        # salvar o pdf na pasta
        urllib.request.urlretrieve(
            url_correspondencia
            + "retrieve/"
            + processo["anexo"][0]["arquivo"]
            + "/"
            + token,
            caminho_arquivo,
        )

    print("Pdfs dos ARs baixados com sucessos.")


def logar_site_perfil(nav_driver, base_dados_escolhida, usuario):
    print("\r")
    print("Iniciando processo de abertura do PJe no perfil do servidor ...")
    if base_dados_escolhida == 1:
        nav_driver.get("https://pjes.jfpb.jus.br")
        # 1ª PASSO: ABRIR PJE, SELECIONAR AUTENTICAÇÃO JAVA E FECHAR JANELA POSTERIOR
        clicar_por_xpath(nav_driver, '//*[@id="btnUtilizarApplet"]')
        clicar_por_xpath(
            nav_driver, '//*[@id="panelAmbienteContentDiv"]/div/img')
        # 2ª PASSO: FAZER O LOGIN E CLICAR NO BOTÃO ENTRAR
        digitar_por_id(nav_driver, "login:username", "RXC")
        digitar_por_id(nav_driver, "login:password", "RXC")
        clicar_por_id(nav_driver, "login:btnEntrar")
        WebDriverWait(nav_driver, 60).until(
            ec.url_contains("listViewQuadroAvisoMensagem.seam")
        )
    else:
        nav_driver.get("https://pje.jfpb.jus.br")
        clicar_por_xpath(nav_driver, '//*[@id="btnUtilizarApplet"]')
        clicar_por_xpath(
            nav_driver, "/html/body/div[2]/div[2]/div/div[2]/div/img")
        clicar_por_xpath(nav_driver, '//*[@id="loginAplicacaoButton"]')
        WebDriverWait(nav_driver, 60).until(
            ec.url_contains("listViewQuadroAvisoMensagem.seam")
        )

    time.sleep(10)  # esperar assinar para entrar no PJe

    # 3º PASSO: Escolher o perfil
    try:
        escolher_select_por_xpath(
            nav_driver,
            '//*[@id="papeisUsuarioForm:usuarioLocalizacaoDecoration:usuarioLocalizacao"]',
            usuario["usuario"]["perfil"]["descricao"],
        )
        print("Login no PJe efetuado com sucesso.")
        return True
    except ErroBot:
        print(
            "\nErro: o usuário selecionado não dispõe do perfil informado no backend --> ",
            usuario["usuario"]["perfil"]["descricao"],
        )
        return False


def juntar_ars(nav_driver, base_dados_escolhida, lista_processos, token, id_relatorio):
    print("\nIniciando a iteração para juntar os pdfs dos ARs.")
    janela_principal = nav_driver.window_handles[0]

    # Iteração para juntar os pdfs dos ars
    for processo in lista_processos:

        if base_dados_escolhida == 1:
            nav_driver.get(
                "https://pjes.jfpb.jus.br/pjesuporte/Painel/painel_usuario/list.seam"
            )
        else:
            nav_driver.get(
                "https://pje.jfpb.jus.br/pje/Painel/painel_usuario/list.seam"
            )

        # SALVA O ID DO PROCESSO PARA FAZER O UPDATE NA API
        id_processo = processo["id"]

        # HEADERS
        headers = {"Token": token}

        # SALVA O NUMERO DO PROCESSO
        numero_do_processo = processo["numProcesso"]
        # print("Numero do Processo: " + process)
        # data_correspondencia = processo["data"]
        # print(data_correspondencia)

        # UPDATE HOUVE TENTATIVA DE JUNTADA
        status_bot = "Erro na tentativa"
        correspondencia_data = {
            "status_bot": status_bot,
        }
        url_update = url_correspondencia + str(id_processo)

        # depois ativar essa parte
        requests.put(url_update, json=correspondencia_data, headers=headers)

        # Pesquisar pelo número do processo
        elemento_id_pesquisa = (
            "localizarCaixaForm:idDecoratenumeroProcessoConsulta:numeroProcessoConsulta"
        )
        digitar_por_id(nav_driver, elemento_id_pesquisa,
                       processo["numProcesso"])
        # clica no prim resultado
        clicar_por_xpath(
            nav_driver,
            "/html/body/div[1]/div[1]/div/table/tbody/tr/td/div/table/tbody/tr[1]/td",
        )

        # Clicar no botão detalhe do processo
        clicar_por_id(
            nav_driver,
            "listConsultaProcessoForm:consultaProcessoListPainelUsuario:0:j_id412:j_id423",
        )

        # Mudar para a janela dos detalhes do processo
        time.sleep(5)  # aperfeiçoar com uma checagem da janela
        popup_detalhes_processo = nav_driver.window_handles[1]
        nav_driver.switch_to.window(popup_detalhes_processo)
        nav_driver.maximize_window()
        time.sleep(2.5)
        # Clicar em expedientes
        clicar_por_xpath(nav_driver, '//*[@id="processoExpedienteTab_lbl"]')
        time.sleep(2.5)

        # Iteração na tabela de expedientes
        # Obter o número de páginas
        num_pags: int = 0
        for i in range(30):
            try:
                num_pags = nav_driver.find_element_by_xpath(
                    "/html/body/div[4]/div/table/tbody/tr[2]/td/table/tbody/tr["
                    "2]/td/table/tbody/tr/td/div/div/div[2]/div/div[2]/form/div"
                    "[2]/div[2]/div[1]/div/table/tbody/tr[1]/td[3]"
                ).text
                break
            except NoSuchElementException:
                time.sleep(2)

        num_pags = int(num_pags)
        # print(num_pags)
        if num_pags == 0:
            informar_erro(
                "Não foi possível abrir a janela de expedientes",
                numero_do_processo,
                token,
            )
            continue
        indice_expediente: int = -1
        for i in range(num_pags):
            try:
                WebDriverWait(nav_driver, 30).until(
                    ec.visibility_of_element_located(
                        (
                            By.XPATH,
                            '//*[@id="expedienteformExpediente:expedienteprocessosCadastradosDataTable:tb"]',
                            # mensagem de sucesso xpath
                        )
                    )
                )
            except TimeoutException:
                break  # para a iteração nas páginas de expedientes

            tabela_expedientes = nav_driver.find_element_by_xpath(
                '//*[@id="expedienteformExpediente:expedienteprocessosCadastradosDataTable:tb"]'
            )
            linhas_tabela = len(
                tabela_expedientes.find_elements_by_tag_name("tr"))

            for j in range(linhas_tabela):
                tr = nav_driver.find_element_by_xpath(
                    "/html/body/div[4]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/div/div/div["
                    "2]/div/div[2]/form/div[2]/div[2]/table/tbody/tr[{}]".format(
                        j + 1)
                ).text
                if processo["destinatario"] in tr and processo["data"] in tr:
                    indice_expediente = j
                    break
                    
            # print(indice_expediente)
            if indice_expediente > 0:
                # encontrou
                break  # for in range(num_pags)

            else:
                # se não encontrou vai para a próxima página
                try:
                    proxima = nav_driver.find_element_by_xpath(
                        "//*[@id='expedienteformExpediente:j_id3918ArrowInc']"
                    )
                    proxima.click()
                except NoSuchElementException:
                    informar_erro("Expediente não encontrado",
                                  numero_do_processo, token)
                    continue

                # Testar se a tabela ainda existe
                for _ in range(20):  # aguarda 60 segundos
                    try:
                        tabela_expedientes.is_enabled()
                        time.sleep(1)
                    except StaleElementReferenceException:
                        # deixou de existir, então prossegue
                        break
                # TODO colocar um erro aqui se a tabela existir por tempo superior a 30s

        if indice_expediente < 0:
            # se o índice for -1, é que não encontrou após passar por todas as tabelas disponíveis
            informar_erro("Expediente não encontrado",
                          numero_do_processo, token)
            continue

        # Desmarcar o checkbox do expediente
        WebDriverWait(nav_driver, 30).until(
            ec.visibility_of_element_located(
                (
                    By.XPATH,
                    '// *[ @ id = "expedienteformExpediente:expedienteproce'
                    "ssosCadastradosDataTable:{}:expedientecheckExpedientes"
                    '"]'.format(indice_expediente),
                    # mensagem de sucesso xpath
                )
            )
        )
        check_box_expediente = nav_driver.find_element_by_xpath(
            '// *[ @ id = "expedienteformExpediente:expedienteproce'
            "ssosCadastradosDataTable:{}:expedientecheckExpedientes"
            '"]'.format(indice_expediente)
        )

        if check_box_expediente.get_attribute("checked"):
            check_box_expediente.click()
            clicar_por_xpath(
                nav_driver, '//*[@id="expedienteformExpediente:btnExcluirCadastrados"]'
            )
            time.sleep(2.5)  # esperar um pouco

        # Abrir a janela para elaborar a certidão e juntar o AR
        try:
            clicar_por_xpath(
                nav_driver,
                "//*[@id='expedienteformExpediente:expedienteprocessosCadastradosDataTable:{}:j_id3895']".format(
                    indice_expediente
                ),
            )
        except ErroBot:
            informar_erro(
                "Erro ao tentar clicar no botão de elaborar certidão",
                numero_do_processo,
                token,
            )
            nav_driver.close()
            continue

        # Mudar para a janela da elaboração da certidão
        time.sleep(5)  # aperfeiçoar com uma checagem da janela
        popup_elaborar_certidao = nav_driver.window_handles[2]
        nav_driver.switch_to.window(popup_elaborar_certidao)
        nav_driver.maximize_window()

        # Preencher as informações da certidão
        cumprido = processo["anexo"][0]["cumprido"]
        if cumprido == "1":
            digitar_por_xpath(
                nav_driver,
                "//*[@id='certidaoForm:inputProcessoDocumentoHtmlDecoration:inputProcessoDocumentoHtml']",
                "CERTIDÃO DE JUNTADA DE AR - CUMPRIDO",
            )
            select_modelo_documento = Select(
                nav_driver.find_element_by_xpath(
                    "//*[@id='certidaoForm:modeloDocumentoComboDecoration:modeloDocumentoCombo']"
                )
            )
            select_modelo_documento.select_by_visible_text(
                "ROBO CERTIDÃO JUNTADA AR")
            # clicar_por_xpath(nav_driver, "//*[@id='certidaoForm:cumpridoDecoration:cumprido:0']")
            time.sleep(1.5)
            cumprido = nav_driver.find_element_by_xpath(
                "//*[@id='certidaoForm:cumpridoDecoration:cumprido:0']"
            )
            cumprido.click()
            time.sleep(1.5)
        else:
            digitar_por_xpath(
                nav_driver,
                "//*[@id='certidaoForm:inputProcessoDocumentoHtmlDecoration:inputProcessoDocumentoHtml']",
                "CERTIDÃO DE JUNTADA DE AR - NÃO CUMPRIDO",
            )
            select_modelo_documento = Select(
                nav_driver.find_element_by_xpath(
                    "//*[@id='certidaoForm:modeloDocumentoComboDecoration:modeloDocumentoCombo']"
                )
            )
            select_modelo_documento.select_by_visible_text(
                "ROBO CERTIDÃO JUNTADA AR")
            time.sleep(1.5)
            cumprido = nav_driver.find_element_by_xpath(
                "//*[@id='certidaoForm:cumpridoDecoration:cumprido:1']"
            )
            cumprido.click()
            time.sleep(1.5)

        # Adicionar cabeçalho
        try:
            clicar_por_xpath(
                nav_driver, '//*[@id="certidaoForm:modeloDocumentoDecoration:modeloDocumentoTextArea_AutoCabecalhoButton"]',
        )
        except:
            informar_erro(
                "Erro ao tentar clicar no botão de adicionar cabeçalho",
                numero_do_processo,
                token,
            )
            continue

        # Anexar o PDF do AR
        try:
            clicar_por_xpath(
                nav_driver, "//*[@id='toggleAnexarPdfCertidao_header']")
        except:
            informar_erro(
                "Erro ao tentar clicar no botão de adicionar Certidão",
                numero_do_processo,
                token,
            )
            continue

        for i in range(5):
            try:
                btn_limpar = nav_driver.find_element_by_xpath(
                    '//*[@id="commandLinkLimpar"]'
                )
                btn_limpar.click()
                WebDriverWait(nav_driver, 5).until(ec.alert_is_present())
                alerta = nav_driver.switch_to.alert
                alerta.accept()
                time.sleep(2.5)  # espera um pouco
            except NoSuchElementException:
                # informar_erro('Botão LIMPAR não encontrado', process, token)
                time.sleep(1)

        for i in range(5):
            try:
                clicar_por_xpath(nav_driver, "//*[@id='commandLinkAdicionar']")
            except:
                 informar_erro(
                "Erro ao tentar clicar no botão de adicionar anexo",
                numero_do_processo,
                token,
            )
            continue

        pasta_atual = pathlib.Path(__file__).parent.absolute()
        ar_dir_path = "pdfs_ars"
        caminho_arquivo = (
            os.path.join(pasta_atual, ar_dir_path,
                         processo["numProcesso"]) + ".pdf"
        )

        # * AHK

        nome_janela1 = "Enviar arquivo"
        nome_janela2 = "File Upload"

        ahk_script = """
            DetectHiddenWindows, On
            SetControlDelay -1

            WinWait, {2}, , 10
            if ErrorLevel
            {{
                WinWait, {1}, , 10
                WinHide {1}
            }}

            WinHide {2}

            ControlGet, CaixaTexto, Hwnd,, Edit1, {1}
            ControlSetText, , {0}, ahk_id %CaixaTexto%
            ControlGet, BotaoOk, Hwnd,, Button1, {1}
            ControlClick, , ahk_id %BotaoOk%
            """.format(
            caminho_arquivo, nome_janela1, nome_janela2
        )

        f_ = tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False)
        f_.write(ahk_script)
        f_.close()
        comando_autohotkey = [AHK_PATH, f_.name]
        call(comando_autohotkey, stdout=DEVNULL, stderr=DEVNULL)
        time.sleep(2.5)

        # Escolher o tipo de documento, gravar e assinar
        tipo_de_documento = Select(
            nav_driver.find_element_by_xpath('//*[@id="j_id243:0:tipoDoc"]')
        )
        tipo_de_documento.select_by_visible_text("Aviso de Recebimento - AR")

        # Gravar
        try:
            nav_driver.find_element_by_xpath('//*[@id="j_id337:cadastrar"]')
            clicar_por_xpath(
                nav_driver, '//*[@id="j_id337:cadastrar"]'
            )  # se for a primeira tentativa
        except NoSuchElementException:
            clicar_por_xpath(
                nav_driver, '//*[@id="j_id337:update"]'
            )  # se já tiver conteudo

        # Verificar mensagem de sucesso
        try:
            WebDriverWait(nav_driver, 20).until(
                ec.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[3]/div/div/div[2]/div/form/div[3]/span/div/div[2]/dl/dt/span",
                        # mensagem de sucesso xpath
                    )
                )
            )
        except TimeoutException:
            # algum erro quando assinou
            pass

        # Abrir os anexos novamente
        clicar_por_xpath(
            nav_driver, "//*[@id='toggleAnexarPdfCertidao_header']")
        time.sleep(2.5)
        # Assinar
        for i in range(10):
            if (
                nav_driver.find_element_by_xpath(
                    '//*[@id="formAssinatura:pjeOfficeForm-btn-pjeOfficecertificacao"]'
                ).get_attribute("value")
                == "Assinar Digitalmente"
            ):
                clicar_por_xpath(
                    nav_driver,
                    '//*[@id="formAssinatura:pjeOfficeForm-btn-pjeOfficecertificacao"]',
                )
                continue
        
            else:
                time.sleep(2)
        # assinar_digitalmente = nav_driver.find_element_by_xpath('//*[@id="formAssinatura:pjeOfficeForm-btn-pjeOfficecertificacao"]').click()
        time.sleep(2.5)

        # Verificar mensagem de sucesso
        try:
            WebDriverWait(nav_driver, 20).until(
                ec.visibility_of_element_located(
                    (
                        By.XPATH,
                        "/html/body/div[3]/div/div/div[2]/div/form/div[3]/span/div/div[2]/dl/dt/span",
                        # mensagem de sucesso xpath
                    )
                )
            )
        except TimeoutException:
            # algum erro quando assinou
            print('Chegou')
        #          informar_erro(
        #         "Erro ao tentar assinar digitalmente",
        #         numero_do_processo,
        #         token,)
        pass

        # Atualizar o relatório informando o sucesso
        status_bot = "Sucesso na tentativa"
        correspondencia_data = {
            "status_bot": status_bot,
        }
        requests.put(url_update, json=correspondencia_data, headers=headers)

        descricao = "Juntada de ARs"
        atividade_bot_data = {
            "descricao": descricao,
        }
        requests.put(
            url=url_relatorio_bot + str(id_relatorio),
            json=atividade_bot_data,
            headers=headers,
        )
        # Fechar popups
        nav_driver.close()  # aqui fecha a janela da certidão de juntada de AR
        time.sleep(2.5)
        nav_driver.switch_to.window(popup_detalhes_processo)
        nav_driver.close()  # aqui fecha a janela de detalhes do processo

        # Voltar para a janela principal
        nav_driver.switch_to.window(janela_principal)
        time.sleep(5.0)


def main():
    os.system("cls")

    print("### Bem-vindo ao robô de juntada de ARs ###")
    print("* Desenvolvido pelo Escritório de inovação da JFPB\n")

    # escolher a base de dados
    base_escolhida = int(
        input(
            "Digite 1 para entrar na base de homologação ou 2 para entrar na base de produção: "
        )
    )

    # aqui vamos modificar os endereços com base na escolha e informar a base usada
    print("\n")
    if base_escolhida == 1:
        print("A BASE DE HOMOLOGAÇÃO foi escolhida.")
        # etc
    else:
        print("A BASE DE PRODUÇÃO foi escolhida.")
        # etc

    # conferir se está online
    checar_se_backend_online()

    # verificar as credenciais
    usuario, response_data, status, token = checar_credenciais_backend()

    # obter a lista de processos aptos
    lista_processos, id_relatorio = obter_processos_aptos_juntada(
        response_data, token)

    if not lista_processos:
        print("\n### Até mais ###\n")
        quit()

    # efetuar downloads
    efetuar_download_pdfs(lista_processos, token)

    # abrir o navegador
    options = Options()
    profile = webdriver.FirefoxProfile()
    profile.set_preference('intl.accept_languages', 'pt-BR')
    driver = webdriver.Firefox(
        executable_path=GECKODRIVER_PATH, options=options, firefox_profile=profile)

    WebDriverWait(driver, 60).until(
        ec.number_of_windows_to_be(1)
    )

    driver.maximize_window()

    # logar no site
    logou = logar_site_perfil(driver, base_escolhida, usuario)

    # juntar os ars
    if logou:
        juntar_ars(driver, base_escolhida,
                   lista_processos, token, id_relatorio)

    # esperar um tempo para sair
    print("\n### Fim dos trabalhos ###")
    # time.sleep(10)
    driver.quit()


if __name__ == "__main__":
    if not os.path.isfile(AHK_PATH) or not os.path.isfile(GECKODRIVER_PATH):
        print('Erro: Não foi encontrado o AutoHotkey.exe ou GECKODRIVER.EXE')
        os.system("pause")
    else:
        try:
            main()
        finally:
            os.system("pause")
