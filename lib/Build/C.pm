sub do_system {
    my ($class, $cmd) = @_;

    if (ref $cmd eq 'ARRAY') {
        $class->info(join(' ', @$cmd));
        system(@$cmd) == 0
            or die "Installation failure: @$cmd";
    } else {
        $class->info($cmd);
        system($cmd) == 0
            or die "Installation failure: $cmd";
    }
}

sub symlink_devel_executables {
    my ($class, $bin_dir) = @_;

    for my $executable (glob("$bin_dir/*")) {
        my ($name, $version) = basename( $executable ) =~ m/(.+?)(5\.\d.*)?$/;
        if ($version) {
            my $cmd = "ln -fs $executable $bin_dir/$name";
            $class->info($cmd);
            system($cmd);
        }
    }
}

sub info {
    my ($class, @msg) = @_;
    print @msg, "\n";
}

sub get_dynamic_links {
    my ($class, $path) = @_;

    my @links;
    # readlinkを使用してシンボリックリンクの情報を取得
    if (-l $path) {
        my $target = readlink($path);
        push @links, {
            source => $path,
            target => $target,
            is_broken => !-e $target
        };
    }

    # ディレクトリの場合は再帰的に検索
    if (-d $path) {
        opendir(my $dh, $path) or die "Cannot open directory: $!";
        while (my $entry = readdir($dh)) {
            next if $entry eq '.' || $entry eq '..';
            push @links, $class->get_dynamic_links("$path/$entry");
        }
        closedir($dh);
    }

    return @links;
}

# procfsのmeminfoを取得
sub get_meminfo {
    my ($class) = @_;
    my $meminfo = `cat /proc/meminfo`;
    return $meminfo;
}

# TCPの情報をProcfsから取得してそのうちのdropの値を1秒ごとに表示する
sub get_tcp_info {
    my ($class) = @_;
    my $tcp_info = `cat /proc/net/tcp`;
    return $tcp_info;
}

# メモリ使用量を取得
sub get_memory_usage {
    my ($class) = @_;
    my $meminfo = $class->get_meminfo();  # クラスメソッド呼び出しに修正
    my $memory_usage = `free -m`;
    return $memory_usage;
}

1;
