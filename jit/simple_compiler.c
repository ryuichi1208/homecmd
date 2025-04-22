#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdarg.h>

// トークンの種類
typedef enum
{
    TOKEN_EOF,
    TOKEN_IDENTIFIER,
    TOKEN_NUMBER,
    TOKEN_STRING,
    TOKEN_INCLUDE,
    TOKEN_INT,
    TOKEN_RETURN,
    TOKEN_PRINTF,
    TOKEN_LPAREN,    // (
    TOKEN_RPAREN,    // )
    TOKEN_LBRACE,    // {
    TOKEN_RBRACE,    // }
    TOKEN_SEMICOLON, // ;
    TOKEN_COMMA,     // ,
    TOKEN_QUOTE,     // "
    TOKEN_HASH,      // #
    TOKEN_LT,        // <
    TOKEN_GT,        // >
    TOKEN_UNKNOWN
} TokenType;

// トークン構造体
typedef struct
{
    TokenType type;
    char *value;
    int line;
    int column;
} Token;

// レキサー構造体
typedef struct
{
    char *source;
    int pos;
    int length;
    char current_char;
    int line;
    int column;
    Token **tokens;     // 全トークンを保持する配列
    int token_count;    // トークンの数
    int token_capacity; // トークン配列の容量
} Lexer;

// 現在の文字を取得
char get_current_char(Lexer *lexer)
{
    if (lexer->pos >= lexer->length)
    {
        return '\0';
    }
    return lexer->source[lexer->pos];
}

// 次の文字に進む
void advance(Lexer *lexer)
{
    if (lexer->current_char == '\n')
    {
        lexer->line++;
        lexer->column = 0;
    }
    else
    {
        lexer->column++;
    }

    lexer->pos++;
    lexer->current_char = get_current_char(lexer);
}

// 空白をスキップ
void skip_whitespace(Lexer *lexer)
{
    while (lexer->current_char != '\0' && isspace(lexer->current_char))
    {
        advance(lexer);
    }
}

// コメントをスキップ
void skip_comment(Lexer *lexer)
{
    if (lexer->current_char == '/' && lexer->pos + 1 < lexer->length && lexer->source[lexer->pos + 1] == '/')
    {
        while (lexer->current_char != '\0' && lexer->current_char != '\n')
        {
            advance(lexer);
        }
        if (lexer->current_char == '\n')
        {
            advance(lexer);
        }
    }
}

// 識別子を解析
Token *parse_identifier(Lexer *lexer)
{
    int start = lexer->pos;
    int line = lexer->line;
    int column = lexer->column;

    while (lexer->current_char != '\0' && (isalnum(lexer->current_char) || lexer->current_char == '_'))
    {
        advance(lexer);
    }

    int length = lexer->pos - start;
    char *value = (char *)malloc(length + 1);
    strncpy(value, lexer->source + start, length);
    value[length] = '\0';

    Token *token = (Token *)malloc(sizeof(Token));
    token->value = value;
    token->line = line;
    token->column = column;

    if (strcmp(value, "include") == 0)
    {
        token->type = TOKEN_INCLUDE;
    }
    else if (strcmp(value, "int") == 0)
    {
        token->type = TOKEN_INT;
    }
    else if (strcmp(value, "return") == 0)
    {
        token->type = TOKEN_RETURN;
    }
    else if (strcmp(value, "printf") == 0)
    {
        token->type = TOKEN_PRINTF;
    }
    else
    {
        token->type = TOKEN_IDENTIFIER;
    }

    return token;
}

// 数値を解析
Token *parse_number(Lexer *lexer)
{
    int start = lexer->pos;
    int line = lexer->line;
    int column = lexer->column;

    while (lexer->current_char != '\0' && isdigit(lexer->current_char))
    {
        advance(lexer);
    }

    int length = lexer->pos - start;
    char *value = (char *)malloc(length + 1);
    strncpy(value, lexer->source + start, length);
    value[length] = '\0';

    Token *token = (Token *)malloc(sizeof(Token));
    token->type = TOKEN_NUMBER;
    token->value = value;
    token->line = line;
    token->column = column;

    return token;
}

// 文字列を解析
Token *parse_string(Lexer *lexer)
{
    int line = lexer->line;
    int column = lexer->column;

    advance(lexer); // 開始の " をスキップ

    int start = lexer->pos;
    while (lexer->current_char != '\0' && lexer->current_char != '"')
    {
        advance(lexer);
    }

    int length = lexer->pos - start;
    char *value = (char *)malloc(length + 1);
    strncpy(value, lexer->source + start, length);
    value[length] = '\0';

    if (lexer->current_char == '"')
    {
        advance(lexer); // 終了の " をスキップ
    }

    Token *token = (Token *)malloc(sizeof(Token));
    token->type = TOKEN_STRING;
    token->value = value;
    token->line = line;
    token->column = column;

    return token;
}

// プリプロセッサディレクティブを解析
Token *parse_preprocessor(Lexer *lexer)
{
    int line = lexer->line;
    int column = lexer->column;

    // # を処理
    Token *token = (Token *)malloc(sizeof(Token));
    token->type = TOKEN_HASH;
    token->value = strdup("#");
    token->line = line;
    token->column = column;

    advance(lexer);
    skip_whitespace(lexer);

    // include など、プリプロセッサの種類を取得
    if (lexer->current_char != '\0' && isalpha(lexer->current_char))
    {
        int start = lexer->pos;
        while (lexer->current_char != '\0' && isalnum(lexer->current_char))
        {
            advance(lexer);
        }

        int length = lexer->pos - start;
        char *directive = (char *)malloc(length + 1);
        strncpy(directive, lexer->source + start, length);
        directive[length] = '\0';

        // プリプロセッサディレクティブに応じた処理
        if (strcmp(directive, "include") == 0)
        {
            free(token->value);
            token->type = TOKEN_INCLUDE;
            token->value = malloc(strlen("#include") + 1);
            strcpy(token->value, "#include");

            // 空白をスキップ
            skip_whitespace(lexer);

            // <stdio.h> や "header.h" を処理
            if (lexer->current_char == '<' || lexer->current_char == '"')
            {
                char opener = lexer->current_char;
                char closer = (opener == '<') ? '>' : '"';

                advance(lexer); // < または " をスキップ

                int header_start = lexer->pos;
                while (lexer->current_char != '\0' && lexer->current_char != closer && lexer->current_char != '\n')
                {
                    advance(lexer);
                }

                int header_length = lexer->pos - header_start;
                if (header_length > 0)
                {
                    // ヘッダー名を token->value に追加する
                    char *header_name = (char *)malloc(header_length + 1);
                    strncpy(header_name, lexer->source + header_start, header_length);
                    header_name[header_length] = '\0';

                    char *new_value = (char *)malloc(strlen(token->value) + header_length + 4);
                    sprintf(new_value, "%s %c%s%c", token->value, opener, header_name, closer);

                    free(token->value);
                    token->value = new_value;
                    free(header_name);
                }

                if (lexer->current_char == closer)
                {
                    advance(lexer); // > または " をスキップ
                }
            }
        }

        free(directive);
    }

    // 行末までスキップ
    while (lexer->current_char != '\0' && lexer->current_char != '\n')
    {
        advance(lexer);
    }

    return token;
}

// 次のトークンを取得
Token *get_next_token(Lexer *lexer)
{
    while (lexer->current_char != '\0')
    {
        if (isspace(lexer->current_char))
        {
            skip_whitespace(lexer);
            continue;
        }

        if (lexer->current_char == '/' && lexer->pos + 1 < lexer->length && lexer->source[lexer->pos + 1] == '/')
        {
            skip_comment(lexer);
            continue;
        }

        int line = lexer->line;
        int column = lexer->column;

        if (lexer->current_char == '#')
        {
            return parse_preprocessor(lexer);
        }

        if (isalpha(lexer->current_char) || lexer->current_char == '_')
        {
            return parse_identifier(lexer);
        }

        if (isdigit(lexer->current_char))
        {
            return parse_number(lexer);
        }

        if (lexer->current_char == '"')
        {
            return parse_string(lexer);
        }

        Token *token = (Token *)malloc(sizeof(Token));
        token->value = (char *)malloc(2);
        token->value[0] = lexer->current_char;
        token->value[1] = '\0';
        token->line = line;
        token->column = column;

        switch (lexer->current_char)
        {
        case '(':
            token->type = TOKEN_LPAREN;
            break;
        case ')':
            token->type = TOKEN_RPAREN;
            break;
        case '{':
            token->type = TOKEN_LBRACE;
            break;
        case '}':
            token->type = TOKEN_RBRACE;
            break;
        case ';':
            token->type = TOKEN_SEMICOLON;
            break;
        case ',':
            token->type = TOKEN_COMMA;
            break;
        case '<':
            token->type = TOKEN_LT;
            break;
        case '>':
            token->type = TOKEN_GT;
            break;
        default:
            token->type = TOKEN_UNKNOWN;
            break;
        }

        advance(lexer);
        return token;
    }

    Token *token = (Token *)malloc(sizeof(Token));
    token->type = TOKEN_EOF;
    token->value = NULL;
    token->line = lexer->line;
    token->column = lexer->column;
    return token;
}

// トークンを追加
void add_token(Lexer *lexer, Token *token)
{
    if (lexer->token_count >= lexer->token_capacity)
    {
        lexer->token_capacity *= 2;
        lexer->tokens = (Token **)realloc(lexer->tokens, lexer->token_capacity * sizeof(Token *));
    }

    lexer->tokens[lexer->token_count++] = token;
}

// 全てのトークンを取得する
void tokenize(Lexer *lexer)
{
    Token *token;
    do
    {
        token = get_next_token(lexer);
        add_token(lexer, token);
    } while (token->type != TOKEN_EOF);
}

// レキサーの初期化
Lexer *init_lexer(char *source)
{
    Lexer *lexer = (Lexer *)malloc(sizeof(Lexer));
    lexer->source = source;
    lexer->pos = 0;
    lexer->length = strlen(source);
    lexer->current_char = get_current_char(lexer);
    lexer->line = 1;
    lexer->column = 0;

    // トークン配列の初期化
    lexer->token_capacity = 16;
    lexer->token_count = 0;
    lexer->tokens = (Token **)malloc(lexer->token_capacity * sizeof(Token *));

    return lexer;
}

// レキサーの解放
void free_lexer(Lexer *lexer)
{
    // トークンの解放
    for (int i = 0; i < lexer->token_count; i++)
    {
        if (lexer->tokens[i]->value)
        {
            free(lexer->tokens[i]->value);
        }
        free(lexer->tokens[i]);
    }

    free(lexer->tokens);
    free(lexer);
}

// ファイルを読み込む
char *read_file(const char *filename)
{
    FILE *file = fopen(filename, "rb");
    if (!file)
    {
        printf("ファイルを開けませんでした: %s\n", filename);
        return NULL;
    }

    fseek(file, 0, SEEK_END);
    long length = ftell(file);
    fseek(file, 0, SEEK_SET);

    char *buffer = (char *)malloc(length + 1);
    if (buffer)
    {
        fread(buffer, 1, length, file);
        buffer[length] = '\0';
    }

    fclose(file);
    return buffer;
}

// トークンの種類を文字列に変換
const char *token_type_to_string(TokenType type)
{
    switch (type)
    {
    case TOKEN_EOF:
        return "EOF";
    case TOKEN_IDENTIFIER:
        return "IDENTIFIER";
    case TOKEN_NUMBER:
        return "NUMBER";
    case TOKEN_STRING:
        return "STRING";
    case TOKEN_INCLUDE:
        return "INCLUDE";
    case TOKEN_INT:
        return "INT";
    case TOKEN_RETURN:
        return "RETURN";
    case TOKEN_PRINTF:
        return "PRINTF";
    case TOKEN_LPAREN:
        return "LPAREN";
    case TOKEN_RPAREN:
        return "RPAREN";
    case TOKEN_LBRACE:
        return "LBRACE";
    case TOKEN_RBRACE:
        return "RBRACE";
    case TOKEN_SEMICOLON:
        return "SEMICOLON";
    case TOKEN_COMMA:
        return "COMMA";
    case TOKEN_QUOTE:
        return "QUOTE";
    case TOKEN_HASH:
        return "HASH";
    case TOKEN_LT:
        return "LT";
    case TOKEN_GT:
        return "GT";
    case TOKEN_UNKNOWN:
        return "UNKNOWN";
    default:
        return "???";
    }
}

// パーサー構造体
typedef struct
{
    Token **tokens;      // トークン配列
    int token_count;     // トークン数
    int current_token;   // 現在処理中のトークンのインデックス
    char *assembly_code; // 生成されたアセンブリコード
    int code_size;       // コードサイズ
    int code_capacity;   // コード容量
} Parser;

// パーサーの初期化
Parser *init_parser(Token **tokens, int token_count)
{
    Parser *parser = (Parser *)malloc(sizeof(Parser));
    parser->tokens = tokens;
    parser->token_count = token_count;
    parser->current_token = 0;
    parser->code_capacity = 1024;
    parser->assembly_code = (char *)malloc(parser->code_capacity);
    parser->code_size = 0;
    parser->assembly_code[0] = '\0';
    return parser;
}

// パーサーの解放
void free_parser(Parser *parser)
{
    free(parser->assembly_code);
    free(parser);
}

// エラー処理
void parser_error(Parser *parser, const char *message)
{
    Token *token = parser->tokens[parser->current_token];
    printf("エラー: %s (行: %d, 列: %d)\n", message, token->line, token->column);
    exit(1);
}

// 現在のトークンを取得
Token *get_current_token(Parser *parser)
{
    if (parser->current_token >= parser->token_count)
    {
        return NULL;
    }
    return parser->tokens[parser->current_token];
}

// 次のトークンに進む
void parser_advance(Parser *parser)
{
    if (parser->current_token < parser->token_count)
    {
        parser->current_token++;
    }
}

// トークンタイプをチェック
int check_token_type(Parser *parser, TokenType type)
{
    Token *token = get_current_token(parser);
    if (!token)
    {
        return 0;
    }
    return token->type == type;
}

// トークンタイプが一致することを期待して消費する
void expect_token(Parser *parser, TokenType type, const char *error_message)
{
    if (!check_token_type(parser, type))
    {
        parser_error(parser, error_message);
    }
    parser_advance(parser);
}

// アセンブリコードを追加
void parser_emit(Parser *parser, const char *format, ...)
{
    va_list args;
    va_start(args, format);

    char buffer[256];
    vsnprintf(buffer, sizeof(buffer), format, args);

    int len = strlen(buffer);
    if (parser->code_size + len + 1 > parser->code_capacity)
    {
        parser->code_capacity *= 2;
        parser->assembly_code = (char *)realloc(parser->assembly_code, parser->code_capacity);
    }

    strcat(parser->assembly_code, buffer);
    parser->code_size += len;

    va_end(args);
}

// アセンブリファイルに出力
void output_assembly(Parser *parser, const char *filename)
{
    char asm_filename[256];
    snprintf(asm_filename, sizeof(asm_filename), "%s.asm", filename);

    FILE *file = fopen(asm_filename, "w");
    if (!file)
    {
        printf("アセンブリファイルを作成できませんでした: %s\n", asm_filename);
        return;
    }

    fprintf(file, "%s", parser->assembly_code);
    fclose(file);

    printf("アセンブリコードを生成しました: %s\n", asm_filename);
}

// アセンブリコードをコンパイル（macOS ARM64用）
void compile_assembly(const char *filename)
{
    char asm_filename[256];
    char obj_filename[256];
    char exe_filename[256];
    char as_cmd[512];
    char ld_cmd[512];

    snprintf(asm_filename, sizeof(asm_filename), "%s.asm", filename);
    snprintf(obj_filename, sizeof(obj_filename), "%s.o", filename);
    snprintf(exe_filename, sizeof(exe_filename), "%s_asm_exe", filename);

    // macOS ARM64用のアセンブルとリンクコマンド
    snprintf(as_cmd, sizeof(as_cmd), "as -arch arm64 -o %s %s", obj_filename, asm_filename);
    snprintf(ld_cmd, sizeof(ld_cmd), "ld -o %s %s -lSystem -L/Library/Developer/CommandLineTools/SDKs/MacOSX.sdk/usr/lib -syslibroot /Library/Developer/CommandLineTools/SDKs/MacOSX.sdk -platform_version macos 13.0.0 13.0.0 -arch arm64", exe_filename, obj_filename);

    printf("アセンブリコードをコンパイル中...\n");
    printf("コマンド: %s\n", as_cmd);

    int result = system(as_cmd);
    if (result != 0)
    {
        printf("アセンブルに失敗しました。\n");
        return;
    }

    printf("コマンド: %s\n", ld_cmd);
    result = system(ld_cmd);
    if (result != 0)
    {
        printf("リンクに失敗しました。\n");
        return;
    }

    printf("アセンブリコードのコンパイル完了: %s\n", exe_filename);
    printf("実行するには: ./%s\n", exe_filename);
}

// 関数の前方宣言
void parse_function_body_arm64(Parser *parser);
void parse_statement_arm64(Parser *parser);
void parse_return_statement_arm64(Parser *parser);
void parse_program(Parser *parser);

// プログラム全体の解析
void parse_program(Parser *parser)
{
    // アセンブリのヘッダー（macOS ARM64用）
    parser_emit(parser, ".section __TEXT,__text\n");
    parser_emit(parser, ".global _main\n\n");

    // include文をスキップ
    while (parser->current_token < parser->token_count &&
           check_token_type(parser, TOKEN_INCLUDE))
    {
        parser_advance(parser);
    }

    // 関数宣言を解析
    if (parser->current_token < parser->token_count)
    {
        // INT キーワードをチェック
        if (check_token_type(parser, TOKEN_INT))
        {
            parser_advance(parser);
        }
        else
        {
            parser_error(parser, "関数の戻り値の型が必要です");
        }

        // 関数名をチェック
        if (check_token_type(parser, TOKEN_IDENTIFIER))
        {
            char *function_name = get_current_token(parser)->value;
            if (strcmp(function_name, "main") == 0)
            {
                parser_emit(parser, "_main:\n");
            }
            else
            {
                parser_emit(parser, "_%s:\n", function_name);
            }
            parser_advance(parser);
        }
        else
        {
            parser_error(parser, "関数名が必要です");
        }

        // 引数リスト
        expect_token(parser, TOKEN_LPAREN, "関数名の後に '(' が必要です");
        expect_token(parser, TOKEN_RPAREN, "引数リストの後に ')' が必要です");

        // 関数本体
        parse_function_body_arm64(parser);
    }

    // データセクション（文字列リテラル用）
    parser_emit(parser, "\n.section __TEXT,__cstring,cstring_literals\n");

    // 文字列リテラルを追加
    for (int i = 0; i < parser->token_count; i++)
    {
        if (parser->tokens[i]->type == TOKEN_STRING)
        {
            // 文字列リテラルをデータセクションに追加
            parser_emit(parser, "L_.str%d:\n", i);
            parser_emit(parser, "    .asciz \"%s\"\n", parser->tokens[i]->value);
        }
    }
}

// 関数本体の解析（macOS ARM64用）
void parse_function_body_arm64(Parser *parser)
{
    expect_token(parser, TOKEN_LBRACE, "関数の始まりに '{' が必要です");

    // 関数プロローグ
    parser_emit(parser, "    stp x29, x30, [sp, #-16]!\n"); // フレームポインタとリンクレジスタを保存
    parser_emit(parser, "    mov x29, sp\n");               // フレームポインタを設定

    // 関数の本体
    while (!check_token_type(parser, TOKEN_RBRACE) && !check_token_type(parser, TOKEN_EOF))
    {
        parse_statement_arm64(parser);
    }

    // 関数エピローグ（明示的なreturnがない場合）
    if (!check_token_type(parser, TOKEN_EOF))
    {
        parser_emit(parser, "    mov w0, #0\n"); // デフォルトで0を返す
        parser_emit(parser, "    ldp x29, x30, [sp], #16\n");
        parser_emit(parser, "    ret\n");
    }

    expect_token(parser, TOKEN_RBRACE, "関数の終わりに '}' が必要です");
}

// 文の解析（macOS ARM64用）
void parse_statement_arm64(Parser *parser)
{
    if (check_token_type(parser, TOKEN_RETURN))
    {
        parse_return_statement_arm64(parser);
    }
    else if (check_token_type(parser, TOKEN_PRINTF))
    {
        // printf関数呼び出し
        parser_advance(parser);
        expect_token(parser, TOKEN_LPAREN, "printf の後に '(' が必要です");

        if (check_token_type(parser, TOKEN_STRING))
        {
            int str_index = parser->current_token;
            parser_emit(parser, "    adrp x0, L_.str%d@PAGE\n", str_index);
            parser_emit(parser, "    add x0, x0, L_.str%d@PAGEOFF\n", str_index);
            parser_emit(parser, "    bl _printf\n");
            parser_advance(parser);
        }
        else
        {
            parser_error(parser, "printf には文字列が必要です");
        }

        expect_token(parser, TOKEN_RPAREN, "printf の引数リストの後に ')' が必要です");
        expect_token(parser, TOKEN_SEMICOLON, "printf 文の後にセミコロンが必要です");
    }
    else
    {
        parser_error(parser, "不明な文です");
    }
}

// return文の解析（macOS ARM64用）
void parse_return_statement_arm64(Parser *parser)
{
    expect_token(parser, TOKEN_RETURN, "return キーワードが必要です");

    // return の後に式が続く場合
    if (!check_token_type(parser, TOKEN_SEMICOLON))
    {
        if (check_token_type(parser, TOKEN_NUMBER))
        {
            char *value = get_current_token(parser)->value;
            parser_emit(parser, "    mov w0, #%s\n", value);
            parser_advance(parser);
        }
        else
        {
            parser_error(parser, "サポートされていない式です");
        }
    }
    else
    {
        // デフォルトで0を返す
        parser_emit(parser, "    mov w0, #0\n");
    }

    parser_emit(parser, "    ldp x29, x30, [sp], #16\n"); // フレームポインタとリンクレジスタを復元
    parser_emit(parser, "    ret\n");                     // 関数から戻る

    expect_token(parser, TOKEN_SEMICOLON, "return 文の後にセミコロンが必要です");
}

int main(int argc, char **argv)
{
    if (argc < 2)
    {
        printf("使用法: %s <ソースファイル>\n", argv[0]);
        return 1;
    }

    char *source = read_file(argv[1]);
    if (!source)
    {
        return 1;
    }

    // 入力ファイル名から拡張子を除いたベース名を取得
    char base_filename[256];
    strcpy(base_filename, argv[1]);
    char *dot = strrchr(base_filename, '.');
    if (dot)
    {
        *dot = '\0';
    }

    Lexer *lexer = init_lexer(source);
    tokenize(lexer);

    printf("ファイル '%s' のトークン解析結果:\n", argv[1]);
    printf("-------------------------------------\n");
    printf("%-15s %-20s %-5s %-5s\n", "タイプ", "値", "行", "列");
    printf("-------------------------------------\n");

    for (int i = 0; i < lexer->token_count; i++)
    {
        Token *token = lexer->tokens[i];
        printf("%-15s %-20s %-5d %-5d\n",
               token_type_to_string(token->type),
               token->value ? token->value : "null",
               token->line,
               token->column);
    }

    // パース・コード生成
    printf("\n構文解析・コード生成を開始します...\n");
    Parser *parser = init_parser(lexer->tokens, lexer->token_count);
    parse_program(parser);

    // アセンブリコードの出力
    output_assembly(parser, base_filename);

    // アセンブリコードをコンパイル
    printf("\nアセンブリコードをコンパイルします...\n");
    compile_assembly(base_filename);

    free(source);
    free_parser(parser);
    free_lexer(lexer);

    return 0;
}
