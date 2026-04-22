# Guia de Configuração do SQL Server CDC

## Visão Geral
Este guia demonstra como configurar Change Data Capture (CDC) no SQL Server e implementar um fluxo de trabalho completo de leitura de dados.

## Pré-requisitos
- SQL Server com suporte a CDC habilitado
- Permissões apropriadas no banco de dados

---

## Etapa 1: Criar Banco de Dados e Tabela

```sql
CREATE DATABASE DATABASE_TESTE;

USE DATABASE_TESTE;

CREATE TABLE CADASTRO_CEP (
    id INT IDENTITY(1,1) PRIMARY KEY,
    cep VARCHAR(8),
    logradouro VARCHAR(200),
    complemento VARCHAR(200),
    unidade VARCHAR(200),
    bairro VARCHAR(200),
    localidade VARCHAR(200),
    uf VARCHAR(2),
    estado VARCHAR(200),
    regiao VARCHAR(200),
    ibge INT,
    ddd INT,
    data_cadastro DATETIME DEFAULT GETDATE(),
    data_atualizacao DATETIME,
    processado BIT DEFAULT 0
);
```

## Etapa 2: Habilitar CDC no Banco de Dados

```sql
USE DATABASE_TESTE;
EXEC sys.sp_cdc_enable_db;
```

## Etapa 3: Habilitar CDC na Tabela

```sql
EXEC sys.sp_cdc_enable_table
    @source_schema = 'dbo',
    @source_name = 'CADASTRO_CEP',
    @role_name = NULL,
    @supports_net_changes = 1;
```

Isso cria automaticamente a tabela de rastreamento de alterações: `cdc.dbo_CADASTRO_CEP_CT`

## Etapa 4: Consultar Alterações do CDC

### Obter todas as alterações:
```sql
DECLARE @from_lsn BINARY(10), @to_lsn BINARY(10);
SET @from_lsn = sys.fn_cdc_get_min_lsn('dbo_CADASTRO_CEP');
SET @to_lsn = sys.fn_cdc_get_max_lsn();

SELECT * FROM cdc.fn_cdc_get_all_changes_dbo_CADASTRO_CEP(@from_lsn, @to_lsn, 'all');
```

### Filtrar registros não processados:
```sql
DECLARE @from_lsn BINARY(10), @to_lsn BINARY(10);

SELECT @from_lsn = ultimo_lsn FROM CDC_CONTROLE WHERE nome_processo = 'CADASTRO_CEP';
SET @to_lsn = sys.fn_cdc_get_max_lsn();

SELECT * FROM cdc.fn_cdc_get_all_changes_dbo_CADASTRO_CEP(@from_lsn, @to_lsn, 'all')
WHERE processado = 0;
```

## Etapa 5: Testar CDC

```sql
INSERT INTO CADASTRO_CEP(cep) VALUES('90050080');
```

---

## Fluxo de Trabalho Completo do CDC

### Criar Tabela de Controle

```sql
CREATE TABLE CDC_CONTROLE (
    id INT IDENTITY PRIMARY KEY,
    nome_processo VARCHAR(100),
    ultimo_lsn BINARY(10),
    data_execucao DATETIME DEFAULT GETDATE()
);

INSERT INTO CDC_CONTROLE (nome_processo, ultimo_lsn)
VALUES ('CADASTRO_CEP', sys.fn_cdc_get_min_lsn('dbo_CADASTRO_CEP'));
```

### Consulta do Worker

```sql
DECLARE @from_lsn BINARY(10), @to_lsn BINARY(10);

SELECT @from_lsn = ultimo_lsn FROM CDC_CONTROLE WHERE nome_processo = 'CADASTRO_CEP';
SET @to_lsn = sys.fn_cdc_get_max_lsn();

SELECT cep FROM cdc.fn_cdc_get_all_changes_dbo_CADASTRO_CEP(@from_lsn, @to_lsn, 'all')
WHERE processado = 0;
```

### Atualizar Tabela de Controle

Após processar alterações (Redis/RabbitMQ), atualize o LSN:

```sql
DECLARE @to_lsn BINARY(10);
SELECT @to_lsn = sys.fn_cdc_get_max_lsn();
INSERT INTO CDC_CONTROLE (nome_processo, ultimo_lsn) VALUES ('CADASTRO_CEP', @to_lsn);
```

