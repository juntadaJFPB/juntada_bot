from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
import time
import unittest
import requests
import os
import urllib.request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from ahk import AHK
from datetime import datetime
# import random
# from selenium.webdriver.common import keys


status = 0
while status <= 0:
    print(
        'Digite {1} para entrar na base de teste ou {2} Para entrar na Sistema')
    sistemaEntrada = int(input())
    print('Digite o nome do Usuario..')
    nome = input()
    print('senha..')
    senha = input()
    url = 'http://localhost:3000/api/usuarios/login'
    url_correspondencia = 'http://localhost:3000/api/correspondencia/'
    url_relatorio_bot = 'http://localhost:3000/api/relatorio/'
    url_relatorio_erro = 'http://localhost:3000/api/relatorio_erros/'
    user_data = {
        "senha": senha,
        "username": nome
    }

    response = requests.post(url=url, json=user_data)

    usuario = response.json()
    if response.status_code >= 200 and response.status_code <= 299:
        print('>>>>>>status<<<<<<<<<<')
        # status do while se for diferente de 200 ele volta e pergunta login e senha ate ser 200
        status = response.status_code
        print(response.status_code)
        response_data = response.json()
        token = response_data['token']
        print(response_data)
        print('>>>>>>token<<<<<<<<<<')
        print(token)

        with open('token.txt', 'w') as file:
            file.write(token)

        headers = {
          'Token': token
        }

        request = requests.get(url_correspondencia, headers=headers)
        processos_data = request.json()
        processos = processos_data['correspondencia']

        lista1 = []
        listaProcesso = []
        txt = []
        x = processos
        i = 0

        while i < len(x):
            lista1.append({'id': processos[i]['id'], 'numProcesso': processos[i]['numero_processo'], 'destinatario': processos[i]['destinatario'],
                        'status_bot': processos[i]['status_bot'], 'status': processos[i]['status'], 'data': processos[i]['data'], 'anexo': processos[i]['anexo']})

            i += 1

        i = 0

        while i < len(lista1):
            if((lista1[i]['status_bot'] == 'Ainda nao houve tentativa') and (lista1[i]['status'] != 'Nao Upado')):
                listaProcesso.append({'id': processos[i]['id'], 'numProcesso': lista1[i]
                    ['numProcesso'], 'destinatario': lista1[i]['destinatario'], 'data': lista1[i]['data'], 'status_bot': processos[i]['status_bot'], 'anexo': lista1[i]['anexo'],
                    'CUMPRIDO': lista1[i]['anexo'][0]['cumprido']
                    })

            i += 1
        print(listaProcesso)

        # DIRETORIOS - MUITA ATENÇÃO COM AS BARRAS (AS BARRAS E CONTRABARRAS NÃO DEVEM SER SUBSTITUIDAS)
        diretorio = r"C:\processos\\"
        diretorio_arquivo_upado = ('C:/processos/')
        caminho_ahk = "C:\\Users\\Victor\\Desktop\\AutoHotkey\\AutoHotkey.exe"

        if os.path.exists(diretorio):
            print('Diretorio Existe')
        else:
            os.mkdir(diretorio)

        descricao = "Juntada de ARs"
        id_usuario = response_data["usuario"]["id"]
        numero_juntadas = len(listaProcesso)
        atividadeBot_data = {
            "descricao": descricao,
            "usuario_id": id_usuario,
            "numero_juntadas": numero_juntadas,
        }

        atividade = requests.post(url=url_relatorio_bot, json=atividadeBot_data, headers=headers)
        relatorio_data = atividade.json()
        id_relatorio = relatorio_data['relatorio']['id']
        print(id_relatorio)

        class usando_unittest(unittest.TestCase):
            def setUp(self):
                self.driver = webdriver.Firefox()

            def test_buscar(self):
                driver = self.driver
                if sistemaEntrada == 1:
                    driver.get("https://pjes.jfpb.jus.br")
                else:
                    driver.get("https://pje.jfpb.jus.br/pje/login.seam")

                window_before = driver.window_handles[0]
                print(driver.title)
                ahk = AHK(executable_path=caminho_ahk)

                window_before_title = driver.title
                print(">>>>>>><<<<<<<<<")

                print(window_before_title)

                time.sleep(10)

                if sistemaEntrada == 1:
                # 1ª PASSO: ABRIR PJE, SELECIONAR AUTENTICAÇÃO JAVA E FECHAR JANELA POSTERIOR
                    driver.find_elements_by_xpath(
                    '//*[@id="btnUtilizarApplet"]')[0].click()
                    time.sleep(5)

                    driver.find_elements_by_xpath(
                    '//*[@id="panelAmbienteContentDiv"]/div/img')[0].click()
                    # 2ª PASSO: FAZER O LOGIN E CLICAR NO BOTÃO ENTRAR
                    login = driver.find_elements_by_id('login:username')[0]
                    login.send_keys("RXC")

                    senha = driver.find_elements_by_id('login:password')[0]
                    senha.send_keys("RXC")

                    driver.find_elements_by_id('login:btnEntrar')[0].click()
                    time.sleep(20)
                else:
                    driver.find_elements_by_xpath(
                    '//*[@id="btnUtilizarApplet"]')[0].click()
                    time.sleep(3)
                    driver.find_elements_by_xpath(
                        '//*[@id="/html/body/div[2]/div[2]/div/div[2]/div/img"]')[0].click()
                    time.sleep(5)
                    driver.find_elements_by_xpath(
                        '//*[@id="loginAplicacaoButton"]').click()

                # 3ª PASSO: SELECIONAR A VARA DO SERVIDOR
                select = Select(driver.find_element_by_xpath(
                    '//*[@id="papeisUsuarioForm:usuarioLocalizacaoDecoration:usuarioLocalizacao"]'))
                select.select_by_visible_text(usuario['usuario']['perfil'])

                time.sleep(2.5)

                # 4ª PASSO: SELECIONAR PAINEL DE USUARIO E CLICAR NO ELEMENTO
                # driver.find_elements_by_id('formMenuPainel:menuPainel_span')[0].click()
                # time.sleep(5)
                # driver.find_elements_by_id(
                #     'formMenuPainel:paginaPainelUsuario:anchor')[0].click()
                # time.sleep(10)
                data_e_hora_atuais = datetime.now()
                for i in range(5):
                 try:
                    driver.find_elements_by_id(
                        'formMenuPainel:menuPainel_span')[0].click()
                    time.sleep(1.0)
                    driver.find_elements_by_id(
                    'formMenuPainel:paginaPainelUsuario:anchor')[0].click()
                    time.sleep(2.5)
                    break
                 except:
                        descricao_erro = "Perfil não encontrado"
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                        relatorio = {
                            "descricao" : descricao_erro,
                            "data_hora" :data_e_hora_em_texto,
                            }
                        requests.post(url=url_relatorio_erro, json=relatorio, headers=headers)
                        pass

                # INTERAÇÃO PARA BUSCAR OS PROCESSOS NO PJE
                i = 0
                while i < len(listaProcesso):
                    # SALVA O ID DO PROCESSO PARA FAZER O UPDATE NA API
                    id_processo = listaProcesso[i]['id']

                    # SALVA O NUMERO DO PROCESSO
                    process = listaProcesso[i]['numProcesso']
                    print("Numero do Processo: " + process)
                    data_correspondencia = listaProcesso[i]['data']
                    print(data_correspondencia)

                    # UPDATE HOUVE TENTATIVA DE JUNTADA
                    status_bot = "Houve Tentativa"
                    correspondencia_data = {
                        "status_bot": status_bot,
                    }
                    url_update = (url_correspondencia+str(id_processo))
                    requests.put(url_update, json=correspondencia_data,headers=headers)
                    
                    # CAMINHO DO DIRETORIO
                    caminho = (diretorio+process+'.pdf')
                   
                    # SALVA O ARQUIVO NA PASTA DESIGNADA
                    salvar_processo = urllib.request.urlretrieve(
                        url_correspondencia+'retrieve/'+listaProcesso[i]['anexo'][0]['arquivo']+'/'+token, caminho)
                    # url_correspondencia
                    time.sleep(2.5)

                    # PESQUISA O NUMERO DO PROCESSO NO PJE
                    # numero_processo = driver.find_elements_by_id(
                    #     'localizarCaixaForm:idDecoratenumeroProcessoConsulta:numeroProcessoConsulta')[0]
                    # numero_processo.clear()
                    # time.sleep(2.5)
                    # numero_processo.send_keys(
                    #     listaProcesso[i]['numProcesso'])  # processos
                    # time.sleep(10)

                    # numero_processo.send_keys(Keys.ENTER)
                    # time.sleep(15)

                    try:
                        numero_processo = driver.find_elements_by_id(
                            'localizarCaixaForm:idDecoratenumeroProcessoConsulta:numeroProcessoConsulta')[0]
                        numero_processo.clear()
                        time.sleep(2.5)
                        numero_processo.send_keys(
                            listaProcesso[i]['numProcesso'])  # processos
                        time.sleep(10)

                        numero_processo.send_keys(Keys.ENTER)
                        time.sleep(15)
                    except:
                        descricao_erro = "Processo não encontrado"
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                        relatorio = {
                            "descricao" : descricao_erro,
                            "data_hora" :data_e_hora_em_texto,
                            "numero_processo": process,
                            "data_correspondencia": data_correspondencia
                            }
                        requests.post(url=url_relatorio_erro, json=relatorio, headers=headers)
                        time.sleep(2.5)
                        i+=1
                        pass

                    # DETALHES DO PROCESSO
                    detalhesdoProcesso = driver.find_element_by_id(
                        'listConsultaProcessoForm:consultaProcessoListPainelUsuario:0:j_id412:j_id423')
                    time.sleep(1.5)
                    detalhesdoProcesso.click()
               
 

                    window_after = driver.window_handles[1]
                    driver.switch_to.window(window_after)
                    time.sleep(5)
                    driver.maximize_window()
                    time.sleep(5.0)

                    # EVENTO CLICK EM EXPEDIENTES
                    expediente = driver.find_element_by_id(
                        'processoExpedienteTab_lbl')
                    expediente.click()
                    time.sleep(7)

                    # FAZ A INTERAÇÃO NA TABELA EXPEDIENTES E CLICA NO CHECKBOX
                    rows = len(driver.find_elements_by_xpath('//*[@id="expedienteformExpediente:expedienteprocessosCadastradosDataTable:tb"]/tr'))
                    time.sleep(5)
                    print(rows)
                    j = 0
                    while j < rows:
                        tr = driver.find_element_by_xpath(
                            "/html/body/div[4]/div/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/div/div/div[2]/div/div[2]/form/div[2]/div[2]/table/tbody/tr["+str(j+1)+"]").text

                        if listaProcesso[i]['destinatario'] and listaProcesso[i]['data'] in tr:
                    
                            print('-------------------')
                            # print('aqui')
                            indice = j

                        j+=1
                    print(indice)

                    # print(indice)
                    print(listaProcesso[i]['destinatario'])
                    print(listaProcesso[i]['data'])
                    
                    # CHECKBOX EXPEDIENTES
                    # checkbox = driver.find_element_by_xpath("//*[@id='expedienteformExpediente:expedienteprocessosCadastradosDataTable:"+str(indice)+":j_id3659']")
                    # checkbox.click()
                    # time.sleep(5)
                    try:
                        checkbox = driver.find_element_by_xpath("//*[@id='expedienteformExpediente:expedienteprocessosCadastradosDataTable:"+str(indice)+":j_id3659']")
                        checkbox.click()
                        time.sleep(5)
                    except:
                        i+=1
                        driver.close()
                        driver.switch_to.window(window_before)
                        time.sleep(10)
                        continue

   
                    # ELABORAR CERTIDÃO
                    try:
                        eleb_certidao = driver.find_element_by_xpath("//*[@id='expedienteformExpediente:expedienteprocessosCadastradosDataTable:"+str(indice)+":j_id3895']")
                        eleb_certidao.click()
                    except:
                        descricao_erro = "Elaborar Certidão não encontrado"
                        # data_e_hora_atuais = datetime.now()
                        data_e_hora_em_texto = data_e_hora_atuais.strftime('%d/%m/%Y %H:%M')
                        print(data_e_hora_em_texto)
                        relatorio = {
                            "descricao" : descricao_erro,
                            "data_hora" :data_e_hora_em_texto,
                            "numero_processo": process,
                            "data_correspondencia": data_correspondencia
                            }
                        print(relatorio)
                        requests.post(url=url_relatorio_erro, json=relatorio, headers=headers)

                        i+=1
                        driver.close()
                        driver.switch_to.window(window_before)
                        time.sleep(10)
                        continue

                    window_after2 = driver.window_handles[2]
                    driver.switch_to.window(window_after2)
                    driver.maximize_window()
                    time.sleep(10)

                    # POP-UP WINDOWS 3, PROCESSO PARA FAZER O UPLOAD DO ARQUIVO 
                    digite = driver.find_element_by_xpath(
                        "//*[@id='certidaoForm:inputProcessoDocumentoHtmlDecoration:inputProcessoDocumentoHtml']")
                    digite.send_keys("CERTIDÃO DE JUNTADA DE AR")
                    time.sleep(2.5)

                    selectModDocumento = Select(driver.find_element_by_xpath(
                        "//*[@id='certidaoForm:modeloDocumentoComboDecoration:modeloDocumentoCombo']"))
                    selectModDocumento.select_by_visible_text('Juntada')
                    time.sleep(2.5)
                    
                    # VERIFICA SE O EXPEDIENTE FOI CUMPRIDO
                    if listaProcesso[i]['anexo'][0]['cumprido'] == "1":
                        cumprido = driver.find_element_by_xpath("//*[@id='certidaoForm:cumpridoDecoration:cumprido:0']")
                        cumprido.click()
                    else:
                        cumprido = driver.find_element_by_xpath("//*[@id='certidaoForm:cumpridoDecoration:cumprido:1']")
                        cumprido.click()

                    # ABRE O ANEXO PARA O UPLOAD DO ARQUIVO
                    abriAnexo = driver.find_element_by_xpath(
                        "//*[@id='toggleAnexarPdfCertidao_header']")
                    abriAnexo.click()
                    time.sleep(5)
                    addAnexo = driver.find_element_by_xpath(
                        "//*[@id='commandLinkAdicionar']")
                    addAnexo.click()

                    # CAMINHO DO ARQUIVO, COM UM REPLACE PORQUE A POP-UP DO WINDOWS NÃO RECONHECE "/"
                    WORD_FILE_PATH = (diretorio_arquivo_upado+process)
                    caminhoAtual = WORD_FILE_PATH.replace("/", "\\")
        
                    # print(caminhoAtual)
                    anexo = driver.find_element_by_xpath('//*[@id="commandLinkAdicionar"]').click()

                    # CÓDIGO DO AUTOHOTKEY
                    nome_janela = "Enviar arquivo"
                    ahk_script = """
                        DetectHiddenWindows, On        
                        SetControlDelay -1
                
                        WinWait, {1}, , 10
                        WinHide {1}
                
                        ControlGet, CaixaTexto, Hwnd,, Edit1, {1}
                        ControlSetText, , {0}, ahk_id %CaixaTexto%        
                        ControlGet, BotaoOk, Hwnd,, Button1, {1}
                        ControlClick, , ahk_id %BotaoOk%        
                        """.format(caminhoAtual, nome_janela)

                    time.sleep(5)

                    ahk.run_script(ahk_script, blocking=True)
                    time.sleep(5)
                    tipo_de_documento = Select(driver.find_element_by_xpath('//*[@id="j_id243:0:tipoDoc"]'))
                    tipo_de_documento.select_by_visible_text('Aviso de Recebimento - AR')
                    time.sleep(3)
                    # driver.save_screenshot("C:/Users/Victor/Desktop/processos/%s" % listaProcesso[i]['numProcesso']+'.png')
                    # time.sleep(3)

                    gravar = driver.find_element_by_xpath('//*[@id="j_id337:cadastrar"]')
                    print("Achou")
                    gravar.click()
                    time.sleep(10)
                    assinar_digitalmente = driver.find_element_by_xpath('//*[@id="formAssinatura:pjeOfficeForm-btn-pjeOfficecertificacao"]').click()
                    time.sleep(5)
  
                    time.sleep(2.5)
                    # SE TUDO OCORRER COMO PREVISTO, ELE FAZ UM UPDATE NA API COM O SUCESSO DO UPLOAD DO ARQUIVO
                    status_bot = "Sucesso"
                    correspondencia_data = {
                        "status_bot": status_bot,
                    }

                    # print("TESTE:"+listaProcesso[i]['status_bot'])
                    url_update = (url_correspondencia+str(id_processo))
                    print("Update Concluido com Sucesso")
                    requests.put(url_update, json=correspondencia_data, headers=headers)


                    # ATUALIZACAO BOT
                    descricao = "Juntada ARs"
                    atividadeBot_data = {
                        "descricao": descricao,
                        }
                    atividade = requests.put(url=url_relatorio_bot+str(id_relatorio), json=atividadeBot_data, headers=headers)

                    driver.close()
                    driver.switch_to.window(window_after)
                    time.sleep(2.5)
                    driver.close()

                    driver.switch_to.window(window_before)
                    time.sleep(1.5)
                    
                    # print(listaProcesso[i]['numProcesso'])

                    i += 1
                          
            def tearDown(self):
                self.driver.quit()
                os.system("pause")

        if __name__ == '__main__':
            unittest.main()        
else:
        print("usuario ou senha incorreto")
        print(response.status_code)
        print(response.reason)
       # print(response.text)
