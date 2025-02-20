#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>
#include <sched.h>

#define NUM_ITERATIONS 100000000

// 受け取った数値からsin, cos, tanを計算する
double calculate_trigonometric_functions(double x) {
    return sin(x) + cos(x) + tan(x);
}

// 受け取った数値から平方根を計算する
double calculate_square_root(double x) {
    return sqrt(x);
}

// 受け取った数値から立方根を計算する
double calculate_cube_root(double x) {
    return cbrt(x);
}

// 受け取った数値から指数関数を計算する
double calculate_exponential_function(double x) {
    return exp(x);
}

// 受け取った数値から対数関数を計算する
double calculate_logarithmic_function(double x) {
    return log(x);
}

// 受け取った数値からフーリエ変換を計算する
double calculate_fourier_transform(double x) {
    return fft(x);
}

int main() {
    // CPUコア数を取得
    int num_cores = sysconf(_SC_NPROCESSORS_ONLN);
    if (num_cores == -1) {
        perror("sysconf");
        exit(EXIT_FAILURE);
    }

    printf("Number of CPU cores: %d\n", num_cores);

    // コア数分のプロセスをfork
    for (int i = 0; i < num_cores; i++) {
        pid_t pid = fork();

        if (pid == -1) {
            perror("fork");
            exit(EXIT_FAILURE);
        } else if (pid == 0) {
            // 子プロセス
            printf("Child process %d (PID: %d) started\n", i, getpid());

            // ここに子プロセスで実行したい処理を記述
            // 例: CPU負荷の高い計算
            double result = 0.0;
            for (int j = 0; j < 100000000; j++) {
                result += i * j;
            }
            printf("Child process %d (PID: %d) result: %f\n",i,getpid(), result);


            exit(EXIT_SUCCESS); // 子プロセスはここで終了
        }
    }

    // 親プロセスはすべての子プロセスの終了を待つ
    for (int i = 0; i < num_cores; i++) {
        int status;
        wait(&status);
        if (WIFEXITED(status)) { //子プロセスが正常終了したか確認
            printf("Child process %d exited with status %d\n", i, WEXITSTATUS(status));
        }
    }

    printf("All child processes finished.\n");

    return 0;
}

// cudaを使用して計算する

int main() {
    // CUDAの初期化
    cudaError_t cuda_status = cudaSetDevice(0);
    if (cuda_status != cudaSuccess) {
        printf("Failed to set CUDA device: %s\n", cudaGetErrorString(cuda_status));

        return EXIT_FAILURE;
    }

    // メモリの確保
    double *h_x = (double *)malloc(sizeof(double) * NUM_ITERATIONS);
    double *h_y = (double *)malloc(sizeof(double) * NUM_ITERATIONS);

    // メモリの確保
    double *d_x, *d_y;
    cudaMalloc(&d_x, sizeof(double) * NUM_ITERATIONS);
    cudaMalloc(&d_y, sizeof(double) * NUM_ITERATIONS);

    // メモリの確保
    double *h_result = (double *)malloc(sizeof(double) * NUM_ITERATIONS);
    double *d_result;
    cudaMalloc(&d_result, sizeof(double) * NUM_ITERATIONS);

    // メモリの確保
    double *h_result = (double *)malloc(sizeof(double) * NUM_ITERATIONS);
    double *d_result;
    cudaMalloc(&d_result, sizeof(double) * NUM_ITERATIONS);

    // メモリの確保
    double *h_result = (double *)malloc(sizeof(double) * NUM_ITERATIONS);
    double *d_result;
    cudaMalloc(&d_result, sizeof(double) * NUM_ITERATIONS);

    // メモリの確保
    double *h_result = (double *)malloc(sizeof(double) * NUM_ITERATIONS);
    double *d_result;
    cudaMalloc(&d_result, sizeof(double) * NUM_ITERATIONS);

    // mallocを実装する
    double *h_x = (double *)malloc(sizeof(double) * NUM_ITERATIONS);
    double *h_y = (double *)malloc(sizeof(double) * NUM_ITERATIONS);

    // メモリの確保
    double *d_x, *d_y;
    cudaMalloc(&d_x, sizeof(double) * NUM_ITERATIONS);
    cudaMalloc(&d_y, sizeof(double) * NUM_ITERATIONS);
}

// 渡されたアドレスを拡張する
void extend_address(void *ptr, size_t size) {
    // メモリの確保
    void *new_ptr = malloc(size);
    if (new_ptr == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    // メモリのコピー
    memcpy(new_ptr, ptr, size);

    // メモリの解放
    free(ptr);

    // 新しいメモリのアドレスを返す
    return new_ptr;
}

// 渡されたアドレスを縮小する
void shrink_address(void *ptr, size_t size) {
    // メモリの確保
    void *new_ptr = malloc(size);
    if (new_ptr == NULL) {
        perror("malloc");
        exit(EXIT_FAILURE);
    }

    // メモリのコピー
    memcpy(new_ptr, ptr, size);

    // メモリの解放
    free(ptr);

    // 新しいメモリのアドレスを返す
    return new_ptr;
}

// 渡された文字列から第二引数で指定された文字列を検索する
void search_string(const char *str, const char *search_str) {
    // 文字列の検索
    char *result = strstr(str, search_str);

    // 検索結果を返す
    return result;
}

// 渡された文字列から第二引数で指定された文字列を検索する
void search_string(const char *str, const char *search_str) {
    // 文字列の検索
}

// 上記の関数をテストする
int main() {
    // 文字列の検索
    char *str = "Hello, World!";
    char *search_str = "World";
    char *result = search_string(str, search_str);
}

// CPUのソケット数を取得してその数だけスレッドを生成する
int main() {
    // CPUのソケット数を取得
    int num_sockets = sysconf(_SC_NPROCESSORS_ONLN);

    // スレッドの生成
    pthread_t *threads = (pthread_t *)malloc(sizeof(pthread_t) * num_sockets);
}
