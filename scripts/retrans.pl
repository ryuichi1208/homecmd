#!/usr/bin/perl
use strict;
use warnings;
use IO::Socket::INET;

# --- 対象のリモートホストとポート --- 
# コマンドライン引数で指定（例: ./tcp_syn_procfs.pl 192.168.1.1 80）
my $remote_ip   = $ARGV[0] // '192.168.1.1';
my $remote_port = $ARGV[1] // 80;

# --- TCP接続の試行（内部でSYNを送信） ---
my $socket = IO::Socket::INET->new(
    PeerAddr => $remote_ip,
    PeerPort => $remote_port,
    Proto    => 'tcp',
    Timeout  => 2,
);

if ( !$socket ) {
    print "接続失敗 ($remote_ip:$remote_port): $!\n";
    
    # --- /proc/net/snmp から TCP 再送メトリクスの取得 ---
    if ( open( my $snmp_fh, '<', '/proc/net/snmp' ) ) {
        my @lines = <$snmp_fh>;
        close($snmp_fh);
        
        my ( $tcp_header_line, $tcp_value_line );
        # /proc/net/snmp には "Tcp:" という2行セットがあるので探す
        for ( my $i = 0 ; $i < @lines ; $i++ ) {
            if ( $lines[$i] =~ /^Tcp:\s*(.*)/ ) {
                $tcp_header_line = $1;
                if ( $i + 1 < @lines and $lines[ $i + 1 ] =~ /^Tcp:\s*(.*)/ ) {
                    $tcp_value_line = $1;
                    last;
                }
            }
        }
        
        if ( $tcp_header_line && $tcp_value_line ) {
            my @headers = split( /\s+/, $tcp_header_line );
            my @values  = split( /\s+/, $tcp_value_line );
            my $found   = 0;
            for ( my $i = 0 ; $i < @headers ; $i++ ) {
                if ( $headers[$i] eq 'RetransSegs' ) {
                    print "TCP RetransSegs: $values[$i]\n";
                    $found = 1;
                    last;
                }
            }
            print "RetransSegs フィールドが見つかりませんでした。\n" unless $found;
        }
        else {
            print "TCP メトリクス情報が見つかりませんでした。\n";
        }
    }
    else {
        warn " /proc/net/snmp をオープンできません: $!\n";
    }
}
else {
    print "接続成功 ($remote_ip:$remote_port)\n";
    close($socket);
}
