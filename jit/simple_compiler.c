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
void parse_preprocessor(Lexer *lexer)
{
    // # から始まる行全体をスキップする
    while (lexer->current_char != '\0' && lexer->current_char != '\n')
    {
        advance(lexer);
    }
    if (lexer->current_char == '\n')
    {
        advance(lexer);
    }
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
            Token *token = (Token *)malloc(sizeof(Token));
            token->type = TOKEN_HASH;
            token->value = strdup("#");
            token->line = line;
            token->column = column;
            
            advance(lexer);
            
            // プリプロセッサディレクティブの解析
            skip_whitespace(lexer);
            
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
                    token->value = malloc(strlen("#include") + 1);
                    strcpy(token->value, "#include");
                }
                
                free(directive);
            }
            
            return token;
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
    return lexer;
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

// パーサーの結果構造体
typedef struct
{
    char *assembly_code;
    int code_size;
    int code_capacity;
} Parser;

// パーサーを初期化
Parser *init_parser()
{
    Parser *parser = (Parser *)malloc(sizeof(Parser));
    parser->code_capacity = 1024;
    parser->assembly_code = (char *)malloc(parser->code_capacity);
    parser->code_size = 0;
    parser->assembly_code[0] = '\0';
    return parser;
}

// アセンブリコードを追加
void emit(Parser *parser, const char *format, ...)
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
    
    Lexer *lexer = init_lexer(source);
    
    printf("ファイル '%s' のトークン解析結果:\n", argv[1]);
    printf("-------------------------------------\n");
    printf("%-15s %-20s %-5s %-5s\n", "タイプ", "値", "行", "列");
    printf("-------------------------------------\n");
    
    Token *token;
    do
    {
        token = get_next_token(lexer);
        printf("%-15s %-20s %-5d %-5d\n", 
               token_type_to_string(token->type), 
               token->value ? token->value : "null",
               token->line,
               token->column);
        
        // トークンの解放
        if (token->value)
        {
            free(token->value);
        }
        free(token);
    } while (token->type != TOKEN_EOF);
    
    // コンパイルフェーズは今後実装予定
    printf("\n簡易的なコンパイラです。現在はトークン解析のみ実装しています。\n");
    printf("今後の実装予定：\n");
    printf("1. 構文解析（パーサー）\n");
    printf("2. コード生成\n");
    printf("3. 最適化\n");

    free(source);
    free(lexer);

    return 0;
}
