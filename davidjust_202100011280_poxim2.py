import sys
import struct
def decimal_64bits(valor_decimal):
    # Converte o valor para inteiro
    valor_inteiro = (valor_decimal)

    # Obtém o bit mais significativo
    bit_mais_significativo = (valor_inteiro & (1 << 63)) >> 63

    # Cria um valor de 64 bits repetindo o bit mais significativo
    valor_64bits = (valor_inteiro & 0x7FFFFFFFFFFFFFFF) | ((bit_mais_significativo << 63) * 0xFFFFFFFFFFFFFFFF)

    return int(valor_64bits)
def binario_para_decimal(binario):
    # Verifique se o binário começa com um sinal negativo
    if binario[0] == '-':
        sinal = -1
        binario = binario[1:]  # Remova o sinal negativo
    else:
        sinal = 1

    # Converte o binário para decimal
    decimal = sinal * int(binario, 2)

    return decimal
def decimal_para_binario(numero):
    if numero < 0:
        binario = bin(numero & 0xFFFFFFFF)[2:]  # Remove sinal negativo e estende para 32 bits
    else:
        binario = bin(numero & 0xFFFFFFFF)[2:]  # Remove bits excedentes

    # Estender o bit mais à esquerda, repetindo-o até atingir 32 bits
    while len(binario) < 32:
        binario = binario[0] + binario

    return binario
def decimal_para_hexadecimal(decimal):
    if isinstance(decimal, str) and decimal.lower().startswith("0x"):
        # O valor já está em formato hexadecimal, então retorná-lo intacto
        return decimal
    if isinstance(decimal, float):
        # Converte o número em ponto flutuante para uma string hexadecimal
        packed = struct.pack('>d', decimal)  # '>d' para precisão dupla (64 bits)
        hex_str = ''.join(f'{byte:02X}' for byte in packed)
        return f"0x{hex_str}"
    if decimal >= 0:
        return f"0x{decimal:08X}"
    else:
        hex_repr = hex((1 << 32) + decimal)[3:]  # Representação em complemento de dois
        return f"0x{hex_repr.upper()}"
def decimal_para_hexadecimal_64(decimal):
    if isinstance(decimal, str) and decimal.lower().startswith("0x"):
        # O valor já está em formato hexadecimal, então retorná-lo intacto
        return decimal
    if isinstance(decimal, float):
        decimal = int(decimal)  # Converte o número em ponto flutuante para inteiro
    if decimal >= 0:
        return f"0x{decimal:016X}"
    else:
        hex_repr = hex((2 << 64) + decimal)[3:]  # Representação em complemento de dois
        return f"0x{hex_repr.upper()}"
def exibir_conteudo_memoria(filename):
  MEM32 = []
  with open(filename, 'r') as arquivo_entrada:
    for linha in arquivo_entrada:
      valor_hex = linha.strip()  # Remove espaços em branco e quebras de linha
      valor_decimal = int(valor_hex,
                          16)  # Converte o valor hexadecimal para decimal
      MEM32.append(valor_decimal)
  return MEM32
def complemento_de_2(hex_str, bits=32):
  # Converte a representação hexadecimal em um número inteiro
  num = int(hex_str, 16)

  # Se o bit mais significativo (bit de sinal) for 1, é negativo
  if (num & (1 << (bits - 1))) != 0:
    num = num - (1 << bits)
  else:
    num = num
  return num

def verificar_SR(numero):
    if numero & (1 << 1):  # Verifica se o bit de endereço 1 é 1
        return numero == 24
        print(numero)
    else:
        pass

def main(args):
  # Verificando se a quantidade de argumentos está correta
  if len(args) != 3:
    print("Uso: python nome_do_programa.py arquivo_entrada arquivo_saida")
    return

  # Abrindo o arquivo de entrada com as permissões corretas
  input_file = open(args[1], "r")
  output_filename = args[2]

  # Chamada da função para exibir o conteúdo da memória
  MEM32 = exibir_conteudo_memoria(args[1])
  # Inicializando a pilha
  pilha = []
  # Inicializando o programa
  R = [0] * 32  # O tamanho dos registradores
  def memoria32_para_dict(memoria32):
          mem_dict = {}
          for i, valor in enumerate(memoria32):
              endereco = i * 4
              mem_dict[endereco] = valor
          return mem_dict
  MEM32 =  memoria32_para_dict(MEM32)
  # Abrindo o arquivo de saída
  with open(output_filename, "w") as output_file:
    # Exibindo a inicialização da execução
    output_file.write("[START OF SIMULATION]\n")

    # Configurando a condição de execução como verdadeira
    executa = True

    # Inicializa o dicionário para armazenar as contagens de ocorrências de R[29]
    ocorrencias_R29 = {}

    # Loop principal para simulação
    while executa:
      # Cadeia de caracteres da instrução
      instrucao = ""
      # Dando o "Callock em R[0]"
      R[0] = 0
      # Declarando operandos
      z = 0
      x = 0  
      i = 0
      pc = 0
      l = 0
      # Carregando a instrução de 32 bits (4 bytes) da memória indexada pelo PC (R[29]) no registrador IR (R[28])
      R[28] = MEM32[R[29]]
      # Obtendo o código da operação (6 bits mais significativos)
      opcode = (R[28] & (0b111111 << 26)) >> 26
      # Registradores FPU 

      #Whatchdog
      if R[29] in ocorrencias_R29:
          ocorrencias_R29[R[29]] += 1
      else:
          ocorrencias_R29[R[29]] = 1
      if ocorrencias_R29[R[29]] == 100:
          R[29] = 16
          R[26] = 3786147034
          R[27] = 84
          output_file.write("[HARDWARE INTERRUPTION 1]\n")
      # mov e movs
      if opcode == 0b000000:  # mov
        z = (R[28] & (0b11111 << 21)) >> 21
        xyl = R[28] & 0x1FFFFF
        
        R[z] = (xyl)
        instrucao = f"mov r{z},{xyl}"
        output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=0x{xyl:08X}\n" %
                          instrucao)  
        R[29] = R[29] + 4
      elif opcode == 0b000001:  # movs (mov com sinal)
        z = (R[28] & (0b11111 << 21)) >> 21
        xyl = R[28] & 0x1FFFFF

        # Realizar extensão de sinal para números negativos
        if xyl & 0x100000:  # Verificar o bit de sinal
          xyl = -((xyl ^ 0x1FFFFF) + 1)
        
        R[z] = (xyl)
        instrucao = f"movs r{z},{(xyl)}"  # Exibe o valor com sinal negativo
        output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}={decimal_para_hexadecimal(R[z])}\n" % instrucao)
        if z == 29 and R[z] == 7:  # Verifica se é a instrução de branch incondicional
          executa = False  # movs # movs
        R[29] = R[29] + 4
      # Leitura
      elif opcode == 0b011000:  #l8
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        i = R[28] & 0xFFFF
        def memoria32_para_8(memoria32):
          memoria8 = []

          for valor32 in memoria32:
            # Divide o valor de 32 bits em quatro valores de 8 bits
            valor8_1 = (valor32 >> 24) & 0xFF
            valor8_2 = (valor32 >> 16) & 0xFF
            valor8_3 = (valor32 >> 8) & 0xFF
            valor8_4 = valor32 & 0xFF

            # Adiciona os valores de 8 bits à memória de 8 bits
            memoria8.append(valor8_1)
            memoria8.append(valor8_2)
            memoria8.append(valor8_3)
            memoria8.append(valor8_4)

          return memoria8
        MEM8 = memoria32_para_8(MEM32)
        result = ((R[x] + i))
        R[z] = (MEM8[result])
        # Out - put
        instrucao = f"l8 r{z},[r{x}+{i}]"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=MEM8[R0x{result:08X}]=0x{R[z]:02X}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b011001:  # l16
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        i = R[28] & 0xFFFF

        def memoria32_para_16(memoria32):
          memoria16 = []

          for valor32 in memoria32:
            # Divide o valor de 32 bits em dois valores de 16 bits
            valor16_1 = (valor32 >> 16) & 0xFFFF
            valor16_2 = valor32 & 0xFFFF

            # Adiciona os valores de 16 bits à memória de 16 bits
            memoria16.append(valor16_1)
            memoria16.append(valor16_2)

          return memoria16
        
        MEM16 = memoria32_para_16(MEM32)
        result = ((R[x] + i)*2)
        result_mem = round(result / 2)
        result_z = (MEM16[result_mem])
        R[z] = result_z
        # Out - put
        instrucao = f"l16 r{z},[r{x}+{i}]"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=MEM[0x{result:08X}]=0x{result_z:04X}\n" %
            instrucao)
        R[29] = R[29] + 4     
      elif opcode == 0b011010:  # l32
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        i = R[28] & 0xFFFF

        result = (R[x] + i)*4
        print(result)
        R[z] = (MEM32.get(result))
        # Out - put
        instrucao = f"l32 r{z},[r{x}+{i}]"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=MEM[0x{result:08X}]=0x{R[z]:08X}\n" %
            instrucao)
        R[29] = R[29] + 4
      # Escrita
      elif opcode == 0b011011: #s8
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          i = R[28] & 0xFFFF
          # Função para transformar memória de 32 bits em 8 bits
          def memoria32_para_8(memoria32):
              memoria8 = {}
              for endereco, valor32 in memoria32.items():
                  valor8_1 = (valor32 >> 24) & 0xFF
                  valor8_2 = (valor32 >> 16) & 0xFF
                  valor8_3 = (valor32 >> 8) & 0xFF
                  valor8_4 = valor32 & 0xFF
                  # Adiciona os valores de 8 bits à memória de 8 bits
                  memoria8[endereco] = [valor8_1, valor8_2, valor8_3, valor8_4]
              return memoria8
          # Função para transformar memória de 8 bits em 32 bits
          def memoria8_para_32(memoria8):
              memoria32 = {}
              for endereco, valor8 in memoria8.items():
                  valor32 = (valor8[0] << 24) | (valor8[1] << 16) | (valor8[2] << 8) | valor8[3]
                  memoria32[endereco] = valor32
              return memoria32 
          # Transforma a memória de 32 bits (MEM32) em 8 bits
          memoria8 = memoria32_para_8(MEM32)
          # Obtém o valor de R[z] e o converte para 8 bits
          valor_Rz = R[z] & 0xFF
          # Calcula o endereço na memória de 8 bits
          endereco = (R[x] + i)
          def atualizar_memoria(MEM32, endereco, valor):
            if endereco not in MEM32:
                memoria8[endereco] = [0, 0, 0, valor]
            else:
                memoria8[endereco] = [0, 0, 0, valor]  # Atualiza o valor do endereço existente
            return memoria8  # Retorna o dicionário atualizado
          memoria8 = atualizar_memoria(memoria8, endereco, valor_Rz)
          # Escreve os 8 bits de R[z] na memória de 8 bits no endereço especificado
          # Transforma a memória de 8 bits de volta em 32 bits
          MEM32 = memoria8_para_32(memoria8)
          # Formate a instrução para a saída
          instrucao = f"s8 [r{x}+{i}],r{z}"
          # Escreva a saída no arquivo ou imprima na tela (dependendo de como você está gerenciando a saída)
          output_file.write(
              f"0x{R[29]:08X}:\t%-25s\tMEM[{decimal_para_hexadecimal(endereco)}]=R{z}=0x{valor_Rz:02X}\n" %
              instrucao)
          R[29] = R[29] + 4

      elif opcode == 0b011101: #s32 
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        i = R[28] & 0xFFFF
        endereco = (R[x] + i) * 4
        def atualizar_memoria(MEM32, endereco, valor):
          if endereco not in MEM32:
              MEM32[endereco] = valor
          else:
              MEM32[endereco] = valor  # Atualiza o valor do endereço existente
          return MEM32  # Retorna o dicionário atualizado
        MEM32 = atualizar_memoria(MEM32, endereco, R[z])
        # Formate a instrução para a saída
        instrucao = f"s32 [r{x}+{i}],r{z}"
        # Escreva a saída no arquivo ou imprima na tela (dependendo de como você está gerenciando a saída)
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tMEM[{decimal_para_hexadecimal(endereco)}]=R{z}=0x{R[z]:08X}\n" %
            instrucao)
        R[29] = R[29] + 4
      #Operações de desvio
      elif opcode == 0b101010: #bae
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + 4 + ( i << 2)
          instrucao = f"bae {i}"
          output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC={decimal_para_hexadecimal(result)}\n" % instrucao)
          R[29] = result
      elif opcode == 0b101011: #bat
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + ( i << 2)
          instrucao = f"bat {i}"
          output_file.write(f"0x{(R[29]):08X}:\t%-25s\tPC=0x{(result):08X}\n" % instrucao)
          R[29] = result
      elif opcode == 0b101100: #bbe
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + 4 +( i << 2)
          instrucao = f"bbe {i}"
          output_file.write(f"0x{(R[29]):08X}:\t%-25s\tPC=0x{(result):08X}\n" % instrucao)
          R[29] = result
      elif opcode == 0b101101: #bbt
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + ( i << 2)
          instrucao = f"bbt {i}"
          output_file.write(f"0x{(R[29]):08X}:\t%-25s\tPC=0x{(result):08X}\n" % instrucao)
          R[29] = result
      elif opcode == 0b101110:
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + 4 + ( i << 2)
          instrucao = f"beq {i}"
          output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC={decimal_para_hexadecimal(result)}\n" % instrucao)
          R[29] = result
      elif opcode == 0b101111:
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + 4 + ( i << 2)
          instrucao = f"bge {i}"
          output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC={decimal_para_hexadecimal(result)}\n" % instrucao)
          R[29] = result
      elif opcode == 0b110000:
          i = (R[28] & 0x3FFFFFF)
           
          pc = pc + (i << 2)
          R[29] = pc
          i_value = (decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
          instrucao = f"bgt {i_value}"
          output_file.write(f"0x{pc:08X}:\t%-25s\tPC=0x{R[29]}\n" % instrucao)
          R[29] = R[29] + 4
      elif opcode == 0b110001:
          i = (R[28] & 0x3FFFFFF)
           
          pc = pc + (i << 2)
          R[29] = pc
          i_value = (decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
          instrucao = f"biv {i_value}"
          output_file.write(f"0x{pc:08X}:\t%-25s\tPC=0x{R[29]}\n" % instrucao)
          R[29] = R[29] + 4
      elif opcode == 0b110010:
          i = (R[28] & 0x3FFFFFF)
           
          pc = pc + (i << 2)
          R[29] = pc
          i_value = (decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
          instrucao = f"ble {i_value}"
          output_file.write(f"0x{pc:08X}:\t%-25s\tPC=0x{R[29]}\n" % instrucao)
          R[29] = R[29] + 4
      elif opcode == 0b110011:
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + ( i << 2)
          instrucao = f"blt {i}"
          output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC={decimal_para_hexadecimal(result)}\n" % instrucao)
          R[29] = result
      elif opcode == 0b110100: #bne
          i = (R[28] & 0x3FFFFFF)
          result = R[29] + ( i << 2)
          instrucao = f"bne {i}"
          output_file.write(f"0x{(R[29]):08X}:\t%-25s\tPC=0x{(result):08X}\n" % instrucao)
          R[29] = result
      elif opcode == 0b110101:
          i = (R[28] & 0x3FFFFFF)
           
          pc = pc + (i << 2)
          R[29] = pc
          i_value = (decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
          instrucao = f"bni {i_value}"
          output_file.write(f"0x{pc:08X}:\t%-25s\tPC=0x{R[29]}\n" % instrucao)
          R[29] = R[29] + 4
      elif opcode == 0b110110:
          i = (R[28] & 0x3FFFFFF)
           
          pc = pc + (i << 2)
          R[29] = pc
          i_value = (decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
          instrucao = f"bnz {i_value}"
          output_file.write(f"0x{pc:08X}:\t%-25s\tPC=0x{R[29]}\n" % instrucao)
          R[29] = R[29] + 4
      elif opcode == 0b111000:
          i = (R[28] & 0x3FFFFFF)
           
          pc = pc + (i << 2)
          R[29] = pc
          i_value = (decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
          instrucao = f"bzd {i_value}"
          output_file.write(f"0x{pc:08X}:\t%-25s\tPC=0x{R[29]}\n" % instrucao)
          R[29] = R[29] + 4
      # Bun e Int       
      elif opcode == 0b110111: # bun
        def repeat_bit_26(number):
          # Verifica o valor do bit 26
          bit_26 = number & (1 << 25)
          # Define os bits 27 ao 31 com o valor do bit 26
          if bit_26:
              number |= 0xFE000000  # 0b11111110000000000000000000000000
          else:
              number &= 0x01FFFFFF  # 0b00000001111111111111111111111111
          # Aplica o complemento de dois se o bit mais significativo for 1
          if number & (1 << 31):
              def complemento_de_dois(binario):
                # Adiciona zeros à esquerda para formar grupos de 4 bits
                bits_faltando = 4 - (len(binario) % 4)
                if bits_faltando == 4:
                  bits_faltando = 0
                binario_completado = binario.zfill(len(binario) + bits_faltando)
                # Verifica se o número é negativo (bit mais significativo é 1)
                if binario_completado[0] == '1':
                    # Converte para inteiro considerando complemento de dois
                    valor_decimal = int(binario_completado, 2) - (1 << len(binario_completado))
                else:
                    # Converte para inteiro diretamente
                    valor_decimal = int(binario_completado, 2)
                return valor_decimal
              number = (complemento_de_dois(bin(number)[2:]))
          return number
        R[28] = repeat_bit_26(R[28])
        instrucao = f"bun {R[28]}"
        output_file.write(f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC=0x{(R[29] + (R[28] << 2) + 4):08X}\n" %
                                instrucao)
        if R[28] & 0x3FFFFFF == 0:
          executa = False
        R[29] = R[29] + (R[28] << 2)     
        R[29] = R[29] + 4
      elif opcode == 0b111111: # int
        i = (R[28] & 0x3FFFFFF)
        R[26] = i
        if i == 0:
          R[29] == 0
          executa = False
        instrucao = f"int {i}"
        output_file.write(
                  f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tCR={decimal_para_hexadecimal(R[26])},PC={decimal_para_hexadecimal(R[29])}\n" %
                  instrucao)  # int # int
        R[29] = R[29] + 4
        print(R[29])
      # Operações Aritméticas
      elif opcode == 0b000010: # add
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11
        # Convertendo as strings hexadecimais em inteiros
        R[z] = R[x] + R[y]
        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)  
        #ov
        if (R[x] & (1 << 31)) == (R[y] & (1 << 31)) and (R[z] & (1 << 31)) != (R[x] & (1 << 31)):
            R[31] |= (1 << 3)
        else:
            R[31] &= ~(1 << 3)  
        #CY
        if ((R[z] & (1 << 31)) != 0):
            R[31] |= 1
        else:
            R[31] &= ~1  

        instrucao = f"add r{z}, r{x}, r{y}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}+R{y}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4 
      elif opcode == 0b000011: # sub
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11
        R[z] = R[x] - R[y]

         # Flags específicas
        
        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)  
        #OV
        if (R[x] & (1 << 31)) != (R[y] & (1 << 31)) and (R[z] & (1 << 31)) != (R[x] & (1 << 31)):
            R[31] |= (1 << 3)
        else:
            R[31] &= ~(1 << 3)  
        #CY
        if ((R[z] & (1 << 31)) != 0):
            R[31] |= 1
        else:
            R[31] &= ~1  

        #Out-put
        instrucao = f"sub r{z}, r{x}, r{y}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}-R{y}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4  
      elif opcode == 0b000101: # CMP
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11
        CMP = R[x] - R[y]

        if CMP == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (CMP & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)  
        #OV
        if (R[x] & (1 << 31)) != (R[y] & (1 << 31)) and (CMP & (1 << 31)) != (R[x] & (1 << 31)):
            R[31] |= (1 << 3)
        else:
            R[31] &= ~(1 << 3)  
        #CY
        if ((CMP & (1 << 31)) != 0):
            R[31] |= 1
        else:
            R[31] &= ~1

        #Out-put
        instrucao = f"cmp r{x}, r{y}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tSR=0x{(R[31]):08X}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b000110: # and
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11

        R[z] = R[x] & R[y]
        
        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)

        #Out-put
        instrucao = f"and r{z}, r{x}, r{y}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}&R{y}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b001000: # not
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16

        R[z] = ~R[x]  # Operação de NOT bit a bit
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)
        # Out-put
        instrucao = f"not r{z}, r{x}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=~R{x}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b000111: # or
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11

        R[z] = R[x] or R[y]

        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)
        # Out-put
        instrucao = f"or r{z}, r{x}, r{y}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}|R{y}={decimal_para_hexadecimal(R[z])}, SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)  # or
        R[29] = R[29] + 4
      elif opcode == 0b001001: # xor
        # Registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11

        R[z] = R[x] ^ R[y]
        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)

        # Out-put
        instrucao = f"xor r{z}, r{x}, r{y}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}^R{y}={decimal_para_hexadecimal(R[z])}, SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)  #xor
        R[29] = R[29] + 4
      elif opcode == 0b010010: # addi
        # registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        l = R[28] & 0xFFFF

        if l & (1 << 15):
          l -= (1 << 16)
        if l == 0:
          executa = False
          continue
        R[z] = R[x] + l
        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (R[z] & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)  
        #OV
        if (R[x] & (1 << 31)) == (l & (1 << 15)) and (R[z] & (1 << 31)) != (R[x] & (1 << 31)):
            R[31] |= (1 << 3)
        else:
            R[31] &= ~(1 << 3)  
        #CY
        if ((R[z] & (1 << 31)) != 0 or R[z] == 0):
            R[31] |= 1
        else:
            R[31] &= ~1  
        #Out-put
        instrucao = f"addi r{z}, r{x}, r{l}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}+{decimal_para_hexadecimal(l)}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b010011: # subi
        # registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        l = R[28] & 0xFFFF

        if l & (1 << 15):
          l & (1<<16)
          l -= (1 << 16)
        if l == 0:
          executa = False
          continue
        R[z] = R[x] - (l)

        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        if (R[x] & (1 << 31)) != (l & (1 << 15)) and (R[z] & (1 << 31)) != (R[x] & (1 << 31)):
            R[31] |= (1 << 3)
        else:
            R[31] &= ~(1 << 3)  
        #CY
        if ((R[z] & (1 << 31)) != 0):
            R[31] |= 1
        else:
            R[31] &= ~1  
        #Out-put
        instrucao = f"subi r{z}, r{x}, r{l}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}-{decimal_para_hexadecimal(l)}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b010100: # muli
        # registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        l = R[28] & 0xFFFF

        if l & (1 << 15):
          l -= (1 << 16)
        if l == 0:
          executa = False
          continue
        R[z] = R[x] * l
        #ZN
        if (R[z]) == 0:
             R[31]  |= (1 << 6)
        else:
            R[31]  &= ~(1 << 6)
        #OV
        if ((R[z] & (1 << 31))!= 0):
              R[31] |= (1 << 3)
        else:
              R[31] &= ~(1 << 3)
        #Out-put
        instrucao = f"muli r{z}, r{x}, r{l}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}*{decimal_para_hexadecimal(l)}={decimal_para_hexadecimal(R[z])}, SR=0x{decimal_para_hexadecimal(R[31])}\n" %
            instrucao)  #muli
        R[29] = R[29] + 4
      elif opcode == 0b010101: # divi
        # registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        l = R[28] & 0xFFFF
        def complemento_de_dois(binario):
            # Adiciona zeros à esquerda para formar grupos de 4 bits
            bits_faltando = 4 - (len(binario) % 4)
            if bits_faltando == 4:
               bits_faltando = 0
            binario_completado = binario.zfill(len(binario) + bits_faltando)
            # Verifica se o número é negativo (bit mais significativo é 1)
            if binario_completado[0] == '1':
                # Converte para inteiro considerando complemento de dois
                valor_decimal = int(binario_completado, 2) - (1 << len(binario_completado))
            else:
                # Converte para inteiro diretamente
                valor_decimal = int(binario_completado, 2)

            return valor_decimal
      
        l = (complemento_de_dois(bin(l)[2:]))
       
        if (R[x]) == 0 or l == 0:
          R[z] = 0
        else:
          R[z] = int(R[x] / l)

        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)
          #ZD
        if l == 0:
            R[31] |= (1 << 5)
        else:
            R[31] &= ~(1 << 5)
          #OV
        R[31] &= ~(1 << 3)

        #Out-put
        instrucao = f"divi r{z}, r{x}, {l}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}/{decimal_para_hexadecimal(l)}={decimal_para_hexadecimal(R[z])}, SR=0x{decimal_para_hexadecimal(R[31])}\n" %
            instrucao)
        R[29] = R[29] + 4
      elif opcode == 0b010110: # modi
        # registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        l = R[28] & 0xFFFF
        def complemento_de_dois(binario):
            # Adiciona zeros à esquerda para formar grupos de 4 bits
            bits_faltando = 4 - (len(binario) % 4)
            if bits_faltando == 4:
               bits_faltando = 0
            binario_completado = binario.zfill(len(binario) + bits_faltando)
            # Verifica se o número é negativo (bit mais significativo é 1)
            if binario_completado[0] == '1':
                # Converte para inteiro considerando complemento de dois
                valor_decimal = int(binario_completado, 2) - (1 << len(binario_completado))
            else:
                # Converte para inteiro diretamente
                valor_decimal = int(binario_completado, 2)

            return valor_decimal
        l = (complemento_de_dois(bin(l)[2:]))
        if (R[y]) == 0:
            R[l] = 0
            R[z] = R[x]
        else:
            if R[x] < 0:
              R[z] = (abs(R[x]) % abs(l))
              R[z] = (R[z]) * (-1)
            else :
              R[z] = ((R[x]) % (l))

        #ZN
        if R[z] == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)
        #ZD
        if l == 0:
            R[31] |= (1 << 5)
        else:
            R[31] &= ~(1 << 5)
        #OV
        R[31] &= ~(1 << 3)

        #Out-put
        instrucao = f"modi r{z}, r{x}, {l}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x} mod {decimal_para_hexadecimal(l)}={decimal_para_hexadecimal(R[z])}, SR={decimal_para_hexadecimal(R[31])}\n" %
            instrucao)  #modi
        R[29] = R[29] + 4     
      elif opcode == 0b010111: # CMPI
        # registradores
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        l = R[28] & 0xFFFF

        if l & (1 << 15):
          l -= (1 << 16)
        CMP = R[x] - l

        if CMP == 0:
            R[31] |= (1 << 6)
        else:
            R[31] &= ~(1 << 6)  
        #SN
        if (CMP & (1 << 31)) != 0:
            R[31] |= (1 << 4)
        else:
            R[31] &= ~(1 << 4)  
        #OV
        if (R[x] & (1 << 31)) != (l & (1 << 31)) and (CMP & (1 << 31)) != (R[x] & (1 << 31)):
            R[31] |= (1 << 3)
        else:
            R[31] &= ~(1 << 3)  
        #CY
        if ((CMP & (1 << 31)) != 0):
            R[31] |= 1
        else:
            R[31] &= ~1
          #Out-put
        instrucao = f"cmpi r{x}, {l}"
        output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tSR={decimal_para_hexadecimal(R[31])}\n" %
              instrucao)
        R[29] = R[29] + 4      
      # Sub - rotinas
      elif opcode == 0b001010: # push
        # Identifica os registradores que serão empilhados
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          v = (R[28] & (0b11111 << 6)) >> 6
          w = R[28] & 0b111111
          
          # Associar as variáveis aos valores em R e empilhar
          pares_variaveis_registradores = [(z, R[z]), (x, R[x]), (y, R[y]), (v, R[v]), (w, R[w])]
          pares_variaveis_registradores = [(variavel, valor_registrador) for variavel, valor_registrador in pares_variaveis_registradores if variavel != 0]
          pares_variaveis_registradores = sorted(pares_variaveis_registradores, key=lambda par: par[0])
          # Remove os pares até encontrar um valor diferente de 0 na extremidade direita
          while pares_variaveis_registradores and pares_variaveis_registradores[-1] == 0:
              pares_variaveis_registradores.pop()
          pilha = pares_variaveis_registradores
          # Aplica a função decimal_para_hexadecimal em cada valor do registrador e os coloca entre chaves
          registradores_em_hexa = [f"{decimal_para_hexadecimal(valor_registrador)}" for variavel, valor_registrador in pares_variaveis_registradores]
          valores_formatados = "{" + ",".join(registradores_em_hexa) + "}"

          #Formata os registradores a serem usados
          registradores_usados = {','.join([f'R{variavel}' for variavel, _ in pares_variaveis_registradores])}
          registradores_usados ="{" + ",".join(registradores_usados) + "}"

          #Out-put
          instrucao = f"push {','.join([f'r{variavel}' for variavel, _ in pares_variaveis_registradores])}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tMEM[{decimal_para_hexadecimal(R[30])}]{valores_formatados}={registradores_usados}\n" %
              instrucao)
          R[29] = R[29] + 4
          R[30] = R[30] - (4*(len(pares_variaveis_registradores)))
      elif opcode == 0b001011: # pop
          # Identifica os registradores que serão desempilhados
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          w = (R[28] & (0b11111 << 6)) >> 6
          v = (R[28] & (0b11111 << 0)) >> 0
          # Associar as variáveis aos valores em R e empilhar
          pares_variaveis_registradores = [(z, R[z]), (x, R[x]), (y, R[y]), (v, R[v]), (w, R[w])]
          pares_variaveis_registradores = sorted(pares_variaveis_registradores, key=lambda par: par[0])
           # Verifica se todas as variáveis são iguais a zero
          todas_variaveis_zero = all(variavel == 0 for variavel, _ in pares_variaveis_registradores)
          
          # Atualiza os valores dos registradores com base nos valores da pilha
          for i, (variavel, _) in enumerate(pares_variaveis_registradores):
              for j, par_pilha in enumerate(pilha):
                  if par_pilha[0] == variavel:
                      pares_variaveis_registradores[i] = (variavel, par_pilha[1])
                      del pilha[j]
                      break
          
          # Laço para atualizar os valores dos registradores
          for variavel, valor_registrador in pares_variaveis_registradores:
              R[variavel] = valor_registrador
      
          pares_variaveis_registradores = sorted(pares_variaveis_registradores, key=lambda par: par[0], reverse = True)
          # Remove os valores da variável mais à direita se for zero
          while pares_variaveis_registradores and pares_variaveis_registradores[-1][0] == 0:
              pares_variaveis_registradores.pop()

          # Aplica a função decimal_para_hexadecimal em cada valor do registrador e os coloca entre chaves
          registradores_em_hexa = [f"{decimal_para_hexadecimal(valor_registrador)}" for variavel, valor_registrador in pares_variaveis_registradores]
          valores_formatados = "{" + ",".join(registradores_em_hexa) + "}"

          #Formata os registradores a serem usados
          registradores_usados = {','.join([f'R{variavel}' for variavel, _ in pares_variaveis_registradores])}
          registradores_usados ="{" + ",".join(registradores_usados) + "}"
          if all(variavel == 0 for variavel, _ in pares_variaveis_registradores):
              registradores_usados = "{}"
              valores_formatados = ""
          #Out-put
          instrucao = (f"pop {','.join([f'r{variavel}' for variavel, _ in pares_variaveis_registradores])}"
             if not all(variavel == 0 for variavel, _ in pares_variaveis_registradores)
             else "pop -")
          output_file.write(
                f"{decimal_para_hexadecimal(R[29])}:\t%-25s\t{registradores_usados}=MEM[{decimal_para_hexadecimal(R[30])}]{valores_formatados}\n" %
                instrucao)
          R[29] = R[29] + 4
          R[30] = R[30] - (4*(len(pares_variaveis_registradores)))
      elif opcode == 0b011110: # call
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        i = R[28] & 0xFFFF

        destino = (R[x] + i) << 2
        pc_local = (R[29] + 4)
        
        instrucao = f"call[r{x}+{i}]"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC={decimal_para_hexadecimal(destino)},MEM[{decimal_para_hexadecimal(R[30])}]={decimal_para_hexadecimal(pc_local)}\n" %
            instrucao)
        
        R[29] = (destino)
        R[30] = R[30] - 4

      elif opcode == 0b111001: # call
        i = (R[28] & 0x3FFFFFF)
        
        pc_local = (R[29] + 4)
        i_value = complemento_de_2(decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
        destino = (pc_local + (i_value * 4))
        
        instrucao = f"call {i_value}"
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC={decimal_para_hexadecimal(destino)},MEM[{decimal_para_hexadecimal(R[30])}]={decimal_para_hexadecimal(pc_local)}\n" %
            instrucao)
  
        R[29] = (destino)
        R[30] = R[30] - 4

      elif opcode == 0b011111: # ret
        i = (R[28] & 0x3FFFFFF)
        R[30] = R[30] + 4
        i_value = complemento_de_2(decimal_para_hexadecimal(binario_para_decimal(decimal_para_binario(i))))
        destino = ((pc + ( i_value * 4)) + 4)
        instrucao = f"ret "
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tPC=MEM[{decimal_para_hexadecimal(R[30])}]={decimal_para_hexadecimal(pc_local)}\n" %
            instrucao)
        R[29] = (pc_local)
      #Operações de interrupção 
      elif opcode == 0b100001:  # sbr ou cbr
        # Extrair os valores de z, x e i dos bits correspondentes
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        i = R[28] & 0xFFFF
        # Determinar o nome da instrução com base no valor de i
        nome_instrucao = "sbr" if i == 1 else "cbr"
        if i == 0:
            R[z] &= ~(1 << x)  # Limpa o bit x de R[z]
        else:
            R[z] |= (1 << x)   # Define o bit x de R[z] como 1
        instrucao = f"{nome_instrucao} r{z},[{i}]"  
        # Escrever a saída formatada
        output_file.write(
            f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}={decimal_para_hexadecimal(R[z])}\n" %
            instrucao)
        R[29] = R[29] + 4
      # Operações com bits 10 - 8
      elif opcode == 0b000100:  # Outras instruções baseadas nos bits 10-8
        z = (R[28] & (0b11111 << 21)) >> 21
        x = (R[28] & (0b11111 << 16)) >> 16
        y = (R[28] & (0b11111 << 11)) >> 11
        l = (R[28] & 0b111000) >> 8

        # Extrair bits 10-8
        bits_10_8 = (R[28] & (0b111 << 8)) >> 8

        if bits_10_8 == 0b000:  # mul
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] >> 0) & 0b11111
          R[x] = (R[x]) # Garante sinal extendido
          R[y] = (R[y])  # Garante sinal extendido
          resultado = R[x] * R[y]
          def preencher_64_bits(numero):
            # Verifica se o número é negativo
            msb = '1' if numero < 0 else '0'

            # Converte o número para sua representação binária sem o prefixo '0b'
            numero_binario = bin(abs(int(numero)))[2:]

            # Verifica o comprimento atual da string binária
            comprimento_atual = len(numero_binario)

            # Calcula quantos zeros ou uns são necessários
            zeros_ou_uns_necessarios = 64 - comprimento_atual

            # Preenche a string binária com zeros ou uns à esquerda
            numero_binario_preenchido = msb * zeros_ou_uns_necessarios + numero_binario
            return numero_binario_preenchido
          R[l]= int((preencher_64_bits(resultado)[:32]),2)
          R[z]= int((preencher_64_bits(resultado)[32:]),2)

          #ZN
          if (R[l] or R[z]) == 0:
             R[31]  |= (1 << 6)
          else:
             R[31]  &= ~(1 << 6)  
          #CY
          if (R[l] != 0):
             R[31]  |= 1
          else:
             R[31]  &= ~1  
          
          #Out-put
          instrucao = f"mul r{z}, r{x}, r{y}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{l}:R{z}=R{x}*R{y}=0x{decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
              instrucao)
          R[29] = R[29] + 4
        elif bits_10_8 == 0b001:  # sll
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] & 0b00011111)

          R[z] = abs(R[z])  # Garante sinal extendido
          R[y] = abs(R[y])  # Garante sinal extendido

          resultado = (R[z] << 32 | R[y]) * (2**(l + 1))
          def preencher_64_bits(numero):
            # Verifica se o número é negativo
            msb = '1' if numero < 0 else '0'

            # Converte o número para sua representação binária sem o prefixo '0b'
            numero_binario = bin(abs(int(numero)))[2:]

            # Verifica o comprimento atual da string binária
            comprimento_atual = len(numero_binario)

            # Calcula quantos zeros ou uns são necessários
            zeros_ou_uns_necessarios = 64 - comprimento_atual

            # Preenche a string binária com zeros ou uns à esquerda
            numero_binario_preenchido = msb * zeros_ou_uns_necessarios + numero_binario
            return numero_binario_preenchido
          R[z]= int((preencher_64_bits(resultado)[:32]),2)
          R[x]= int((preencher_64_bits(resultado)[32:]),2)
          #CY
          if (R[z] or R[x]) == 0:
            R[31]  |= (1 << 6)
          else:
            R[31]  &= ~(1 << 6)
          #CY
          if ((R[z]) != 0):
            R[31] |= 1
          else:
            R[31] &= ~1
            
          instrucao = f"sll r{z}, r{x}, r{y}, {l}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}:R{x}=R{z}:R{y}<<{l + 1}={decimal_para_hexadecimal(R[z])}, SR={decimal_para_hexadecimal(R[31])}\n"
              % instrucao)  #sll
          R[29] = R[29] + 4

        elif bits_10_8 == 0b010:  # muls
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] >> 0) & 0b11111
          # Convertendo as strings hexadecimais em inteiros
          R[x] = ((R[x] << 32) >> 32)  # Garante sinal extendido
          R[y] = ((R[y] << 32) >> 32)  # Garante sinal extendido
          
          resultado = R[x] * R[y]
          # Separa os 32 bits mais significativos e menos significativos
          R[l] = (resultado >> 32) & 0xFFFFFFFF
          R[z] = resultado & 0xFFFFFFFF
          #ZN
          if (R[l] or R[z]) == 0:
             R[31] |= (1 << 6)
          else:
             R[31]  &= ~(1 << 6)  
          if (R[l] != 0):
              R[31] |= (1 << 3)
          else:
              R[31] &= ~(1 << 3)

          instrucao = f"muls r{l}, r{z}, r{x}, r{y}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{l}:R{z}=R{x}*R{y}={decimal_para_hexadecimal_64(resultado)},SR={decimal_para_hexadecimal(R[31])}\n" %
              instrucao)  #muls
          R[29] = R[29] + 4
        elif bits_10_8 == 0b011:  # sla
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] & 0b00011111)
          R[z] = abs(R[z])
          R[y] = abs(R[y])
          resultado = (R[z] << 32 | R[y]) * (2**(l + 1))
          def preencher_64_bits(numero):
            # Verifica se o número é negativo
            msb = '1' if numero < 0 else '0'

            # Converte o número para sua representação binária sem o prefixo '0b'
            numero_binario = bin(abs(int(numero)))[2:]

            # Verifica o comprimento atual da string binária
            comprimento_atual = len(numero_binario)

            # Calcula quantos zeros ou uns são necessários
            zeros_ou_uns_necessarios = 64 - comprimento_atual

            # Preenche a string binária com zeros ou uns à esquerda
            numero_binario_preenchido = msb * zeros_ou_uns_necessarios + numero_binario
            return numero_binario_preenchido
          R[z]= int((preencher_64_bits(resultado)[:32]),2)
          R[x]= int((preencher_64_bits(resultado)[32:]),2)
          # Condição 1: Se o resultado for 0, definir o bit 6 como 1
          if resultado == 0:
              R[31] |= (1 << 6)
          else:
              R[31] &= ~(1 << 6)
          # Condição 2: Se R[z] for diferente de 0, definir o bit 3 como 1
          if R[z] != 0:
              R[31] |= (1 << 3)
          else:
              R[31] &= ~(1 << 3)
          instrucao = f"sla r{z}, r{x}, r{y}, {l}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}:R{x}=R{z}:R{x}<<{l + 1}={decimal_para_hexadecimal_64(resultado)}, SR={decimal_para_hexadecimal(R[31])}\n"
              % instrucao)  #sla
          R[29] = R[29] + 4
        elif bits_10_8 == 0b100:  # div
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] & 0b00011111)
          if (R[y]) == 0:
            R[l] = 0
            R[z] = R[x]
          else : 
            R[l] = round(R[x] % R[y])
            R[z] = round(R[x] / R[y])
          #ZN
          if R[z] == 0:
            R[31] |= (1 << 6)
          else:
            R[31] &= ~(1 << 6)
          #ZD
          if R[y] == 0:
            R[31] |= (1 << 5)
          else:
            R[31] &= ~(1 << 5)
          
          if (R[l] != 0 or R[y] == 0):
              R[31] |= 1
          else:
              R[31] &= ~1
          
          #Out-put
          instrucao = f"div r{l}, r{z}, r{x}, r{y}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{l}=R{x} mod R{y}={decimal_para_hexadecimal(R[l])},R{z}=R{x}/R{y}={decimal_para_hexadecimal(R[z])},SR=0x{(R[31]):08X}\n" %
              instrucao)
          R[29] = R[29] + 4
        elif bits_10_8 == 0b101:  # srl
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] & 0b00011111)

          l_valor = (l & 0b11111)
          resultado = int((R[z] << 32 | R[x]) / (2**(l_valor + 1)))
          def preencher_64_bits(numero):
            # Verifica se o número é negativo
            msb = '1' if numero < 0 else '0'

            # Converte o número para sua representação binária sem o prefixo '0b'
            numero_binario = bin(abs(int(numero)))[2:]

            # Verifica o comprimento atual da string binária
            comprimento_atual = len(numero_binario)

            # Calcula quantos zeros ou uns são necessários
            zeros_ou_uns_necessarios = 64 - comprimento_atual

            # Preenche a string binária com zeros ou uns à esquerda
            numero_binario_preenchido = msb * zeros_ou_uns_necessarios + numero_binario
            return numero_binario_preenchido
          R[z]= int((preencher_64_bits(resultado)[:32]),2)
          R[x]= int((preencher_64_bits(resultado)[32:]),2)
          # Separa os 32 bits mais significativos e menos significativos
          R[z] = (resultado >> 32) & 0xFFFFFFFF
          R[x] = resultado & 0xFFFFFFFF

          instrucao = f"srl r{z}, r{x}, r{y}, {l}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}>>{l + 1}={decimal_para_hexadecimal_64(resultado)}\n"
              % instrucao)  # srl
          R[29] = R[29] + 4
        elif bits_10_8 == 0b110:  # divs
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] & 0b00011111)
          def complemento_de_dois(binario):
            # Verifica se o número é negativo (bit mais significativo é 1)
            if binario[0] == '1':
                # Converte para inteiro considerando complemento de dois
                valor_decimal = int(binario, 2) - (1 << len(binario))
            else:
                # Converte para inteiro diretamente
                valor_decimal = int(binario, 2)
            
            return valor_decimal
          R[x] = complemento_de_dois(bin(R[x])[2:])
          R[y] = complemento_de_dois(bin(R[y])[2:])
          if (R[x]) == 0 or (R[y]) == 0:
            R[z] = 0
            R[l] = 0
          else:
            R[z] = round(R[x] / R[y])
            R[l] = int(R[x] % R[y])
          #ZN
          if R[z] == 0:
            R[31] |= (1 << 6)
          else:
            R[31] &= ~(1 << 6)
          #ZD
          if R[y] == 0:
            R[31] |= (1 << 5)
          else:
            R[31] &= ~(1 << 5)
          #OV
          if (R[l] != 0):
              R[31] |= (1 << 3)
          else:
              R[31] &= ~(1 << 3)
          #Out-put
          instrucao = f"divs r{z}, r{x}, r{y}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}=R{x}modR{y}={decimal_para_hexadecimal(R[l])},R{z}=R{x}/R{y}={decimal_para_hexadecimal(R[z])},SR={decimal_para_hexadecimal(R[31])}\n" %
              instrucao)  # divs
          R[29] = R[29] + 4
        elif bits_10_8 == 0b111:  # sra
          z = (R[28] & (0b11111 << 21)) >> 21
          x = (R[28] & (0b11111 << 16)) >> 16
          y = (R[28] & (0b11111 << 11)) >> 11
          l = (R[28] & 0b00011111)
          # Realiza o deslocamento aritmético à esquerda
          R[z] = (R[z])
          R[y] = (R[y])
          l_valor = (l & 0b11111)
          resultado = int((R[z] << 32 | R[y]) / (2**(l_valor + 1)))
        
          def complemento_de_dois(binario):
            # Adiciona zeros à esquerda para formar grupos de 4 bits
            bits_faltando = 4 - (len(binario) % 4)
            if bits_faltando == 4:
               bits_faltando = 0
            binario_completado = binario.zfill(len(binario) + bits_faltando)
            # Verifica se o número é negativo (bit mais significativo é 1)
            if binario_completado[0] == '1':
                # Converte para inteiro considerando complemento de dois
                valor_decimal = int(binario_completado, 2) - (1 << len(binario_completado))
            else:
                # Converte para inteiro diretamente
                valor_decimal = int(binario_completado, 2)

            return valor_decimal
          resultado = complemento_de_dois(bin(resultado)[2:])
          def preencher_64_bits(numero):
            # Verifica se o número é negativo
            msb = '1' if numero < 0 else '0'

            # Converte o número para sua representação binária sem o prefixo '0b'
            numero_binario = bin(abs(int(numero)))[2:]

            # Verifica o comprimento atual da string binária
            comprimento_atual = len(numero_binario)

            # Calcula quantos zeros ou uns são necessários
            zeros_ou_uns_necessarios = 64 - comprimento_atual

            # Preenche a string binária com zeros ou uns à esquerda
            numero_binario_preenchido = msb * zeros_ou_uns_necessarios + numero_binario
            return numero_binario_preenchido
          
          R[z] = int((preencher_64_bits(resultado)[:32]),2)
          R[x] = int((preencher_64_bits(resultado)[32:]),2)

          #CY
          if (R[z] or R[x]) == 0:
            R[31]  |= (1 << 6)
          else:
            R[31]  &= ~(1 << 6)
          #OV
          if (R[z]) != 0:
            R[31]  |= (1 << 3)
          else:
            R[31]  &= ~(1 << 3)
          instrucao = f"sra r{z}, r{x}, r{y}, {l}"
          output_file.write(
              f"{decimal_para_hexadecimal(R[29])}:\t%-25s\tR{z}:R{x}=R{z}:R{x}>>{l + 1}={decimal_para_hexadecimal_64(resultado)},SR={decimal_para_hexadecimal(R[31])}\n"
              % instrucao) # srl
          R[29] = R[29] + 4
        else:
          output_file.write("Instrução desconhecida!\n")
          executa = False
      else:  # Instrução desconhecida
        output_file.write("[SOFTWARE INTERRUPTION]\n")
        R[29] = 12

    # Exibindo o término da simulação
    output_file.write("[END OF SIMULATION]\n")

# Executando a função main
if __name__ == '__main__':
  # Passando os argumentos do programa
  main(sys.argv)