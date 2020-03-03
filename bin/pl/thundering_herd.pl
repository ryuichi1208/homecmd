#!/usr/bin/perl

package EarlyExpiresCache;

use Class::Accessor::Lite (
    new => 1,
    rw  => [ qw(cache ratio early_expires) ],
);

sub set_ee {
    my ($self, $key, $value, $expires) = @_;
    $self->cache->set($key, $value, $expires);
    $self->cache->set($key . "::ee", $value, $expires - $self->early_expires);
}

sub get_ee {
    my ($self, $key) = @_;
    if ( int(rand($self->ratio)) == 0 ) {
        return $self->cache->get($key."::ee");
    }
    $self->cache->get($key) // $self->cache->get($key."::ee")

}

sub delete_ee {
    my ($self, $key) = @_;
    $self->cache->delete($key);
    $self->cache->delete($key."::ee");
}

package main;

my $eecache = EarlyExpiresCache->new(
    early_expires => 60, #sec
    ratio => 10, # 1/10
    cache => Cache::Memcached::Fast->new(...)
);

my $val = $eecache->get_ee('foo');
if ( !$val ) {
    .. heavy sql ..
    $eecache->set_ee('foo', $value, 3600);
}
