use strict;
use warnings;

my $sum = 0;
my $square = 0;
my $n = 0;

my $do_geom = 1;
my $geom = 0;
my $min;
my $max;

while (<>) {
	chomp;
	s#_##g;
	my $x;
	foreach $x (split) {
		next unless $x =~ /^[0-9.+-]+$/;
		$sum += $x;
		$square += $x*$x;
		++$n;
		if ($x <= 0) {
			$do_geom = 0;
		}
		else {
			$geom += log($x);
		}
		$min = $x if (!defined($min) or $x < $min);
		$max = $x if (!defined($max) or $x > $max);
	}
}

my $mean = $sum / $n;
my $sd = sqrt(($square - $sum * $sum / $n) / ($n-1));

if (defined($ENV{'terse'})) {
  printf("count %s min/avg/max %f/%f/%f CV %5.4f%%\n", $n, $min, $mean, $max, 100 * ($sd / $mean));
  exit 0;
}

printf "n:     %10u\n", $n;
printf "total: %15.4f\n", $sum;
printf "mean:  %15.4f\n", $mean;
printf "min:   %15.4f\n", $min;
printf "max:   %15.4f\n", $max;
if ($n > 1) {
        printf "sd:    %15.4f %5.4f%% (coefficient of variation)\n", $sd, 100 * ($sd / $mean);
}

if ($do_geom && $geom != 0) {
	printf "geom:  %15.4f\n", exp($geom/$n);
}
