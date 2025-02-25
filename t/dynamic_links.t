use strict;
use warnings;
use Test::More;
use File::Temp qw(tempdir);
use File::Path qw(make_path);
use Build::C;

# テスト用の一時ディレクトリを作成
my $tmp_dir = tempdir(CLEANUP => 1);

subtest 'シンボリックリンクのテスト' => sub {
    # テスト用のファイルとディレクトリを作成
    my $test_file = "$tmp_dir/test_file";
    my $test_link = "$tmp_dir/test_link";
    my $broken_link = "$tmp_dir/broken_link";

    # テストファイルを作成
    open my $fh, '>', $test_file or die "Cannot create test file: $!";
    print $fh "test content";
    close $fh;

    # 正常なシンボリックリンクを作成
    symlink $test_file, $test_link or die "Cannot create symlink: $!";

    # 壊れたシンボリックリンクを作成
    symlink "$tmp_dir/non_existent_file", $broken_link;

    # リンクの取得をテスト
    my @links = Build::C->get_dynamic_links($tmp_dir);

    # 結果の検証
    my %link_map = map { $_->{source} => $_ } @links;

    # 正常なリンクのテスト
    ok(exists $link_map{$test_link}, '正常なリンクが検出される');
    is($link_map{$test_link}->{target}, $test_file, 'リンク先が正しい');
    ok(!$link_map{$test_link}->{is_broken}, 'リンクは正常');

    # 壊れたリンクのテスト
    ok(exists $link_map{$broken_link}, '壊れたリンクが検出される');
    is($link_map{$broken_link}->{target}, "$tmp_dir/non_existent_file", '壊れたリンクの対象が正しい');
    ok($link_map{$broken_link}->{is_broken}, 'リンクは壊れている');
};

subtest 'ディレクトリ再帰のテスト' => sub {
    # サブディレクトリを作成
    my $sub_dir = "$tmp_dir/subdir";
    make_path($sub_dir);

    # サブディレクトリ内にリンクを作成
    my $sub_file = "$sub_dir/sub_file";
    my $sub_link = "$sub_dir/sub_link";

    open my $fh, '>', $sub_file or die "Cannot create sub file: $!";
    print $fh "sub content";
    close $fh;

    symlink $sub_file, $sub_link;

    # 再帰的な検索をテスト
    my @links = Build::C->get_dynamic_links($tmp_dir);
    my %link_map = map { $_->{source} => $_ } @links;

    ok(exists $link_map{$sub_link}, 'サブディレクトリ内のリンクが検出される');
    is($link_map{$sub_link}->{target}, $sub_file, 'サブディレクトリ内のリンク先が正しい');
    ok(!$link_map{$sub_link}->{is_broken}, 'サブディレクトリ内のリンクは正常');
};

subtest '平方根計算のテスト' => sub {
    # 平方根を計算する関数を定義
    sub calculate_square_root {
        my ($a, $b) = @_;
        return sqrt($a * $b);
    }

    # テストケース
    is(calculate_square_root(4, 9), 6, '4と9の平方根は6');
    is(calculate_square_root(16, 25), 20, '16と25の平方根は20');
    is(sprintf("%.2f", calculate_square_root(2, 3)), '2.45', '2と3の平方根は約2.45');
};

done_testing;
