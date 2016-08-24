#!/usr/bin/perl
use strict;
use CGI "param";

###
### Subroutine declaration
###
sub output_image;
sub read_mandates;
sub mandate_exists;

###
### Main program
###
mkdir '/tmp/webcam' if(!-d '/tmp/webcam');
my $m_path = '/tmp/webcam/mandates.txt';
my $mandate = param('mandate');
die "Mandate not found" if (!$mandate);

my %mandates = read_mandates($m_path);
my $m_found = mandate_exists($m_path, $mandate, %mandates);
if($m_found)
{
	output_image();
}
else
{
	die "Mandate $mandate not found";
}

###
### Subroutine definitions
###
sub read_mandates
{
	my $m_path = shift;
	open (my $mfh, '<', $m_path) or
		die "Cannot open file '$m_path' $!";
	flock($mfh, 1);
	my %mandates;
	while (my $line = <$mfh>)
	{
		chomp $line;
		$mandates{$line} = 1;
	}
	close $mfh;
	return %mandates;
}

sub mandate_exists
{
	my $m_path = shift @_;
	my $mandate = shift @_;
	my %mandates = @_;
	if(exists $mandates{$mandate})
	{

		open (my $mfh, '>', $m_path) or
				die "Cannot open file '$m_path' $!";
		flock($mfh, 2);
		delete $mandates{$mandate};
		foreach my $key (keys(%mandates))
		{
			print $mfh "$key\n";
		}
		close $mfh;
		return 1;
	}
	else
	{
		return 0;
	}
}

sub output_image
{
	mkdir '/tmp/webcam' if(!-d '/tmp/webcam');
	my $dir = '/tmp/webcam/';
	my $file = int(rand(8999)+1000);
	my $ext = '.jpeg';
	my $path = $dir.$file.$ext;

	my $status = system('streamer', '-q', '-o', $path);
	die 'Cannot capture image' if($status);

	print "Content-type: image/jpeg\n\n";

	binmode STDOUT;
	$/=undef;
	open( my $fh, $path);
	my $content = <$fh>;
	print STDOUT $content;
	close $fh;
	unlink $path;
}
