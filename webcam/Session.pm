package Session;

use strict;
use warnings;
use Constants;

sub session_valid
{
        my $sid = shift;
        my %s_hash = read_sessions();
        if(exists $s_hash{$sid})
        {
                if( time() <= $s_hash{$sid})
                {
                        return 'valid';
                }
                else
                {
                        return 'expired';
                }
        }
        else
        {
                return 0;
        }
}

sub read_sessions
{
        my %s_hash;
        open(my $sfh, '<', $Constants::session_path) or die "Cannot open $Constants::session_path $!\n";
        flock( $sfh, 1);
        while(my $line = <$sfh>)
        {
                chomp $line;
                my ($session, $timeout) = split(':', $line);
                $s_hash{$session} = $timeout;
        }
        close $sfh;
        return %s_hash;
}
sub save_sessions
{
        my %s_hash = @_;
        open(my $sfh, '>', $Constants::session_path) or die "Cannot open $Constants::session_path $!\n";
        flock( $sfh, 2);
        foreach my $session (keys %s_hash)
        {
                print $sfh "$session:$s_hash{$session}\n"
        }
        close $sfh;
}

sub update_session
{
        my $sid = shift;
        my %s_hash = read_sessions();

        $s_hash{$sid} += 3600;

        save_sessions(%s_hash);
}

sub remove_session
{
        my $sid = shift;
        my %s_hash = read_sessions();

        my $found = delete $s_hash{$sid};
        die "session not found" if (!$found);

        save_sessions(%s_hash);
}

sub save_session
{
        my $sid = shift;
        my $timeout = 3600 + time();
        open (my $sfh, '>>', $Constants::session_path) or die "Cannot open $Constants::session_path $!\n";
        flock ($sfh, 2); #exclusive lock
        print $sfh "$sid:$timeout\n";
        close $sfh;
}

sub save_mandate
{
        my $mandate = shift @_;
        open (my $mfh, '>>', $Constants::mandate_path) or
                die "Cannot open file '$Constants::mandate_path' $!";
        flock($mfh, 2);
        print $mfh "$mandate\n";
        close $mfh;
}

sub random
{
        my $length = shift;
        my @const = (0..9,'a'..'z','A'..'Z'); # 62 elements, index from 0 to 61
        my @rand = ();
        foreach my $i (0..$length-1)
        {
                $rand[$i] = $const[int(rand(62))];
        }
        return join('',@rand);
}




1;
