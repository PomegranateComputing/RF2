class RFPlayer : PlayerPawn
{
    Default
    {
        Health 100;
        Radius 16;
        Height 56;
        Mass 100;
        PainChance 255;
        Speed 1;
        Player.DisplayName "Viktor Ardent";
        Player.ViewHeight 41;
        Player.AttackZOffset 8;
        Player.JumpZ 8;
        Player.MaxHealth 100;
        Player.ForwardMove 1.0, 1.0;
        Player.SideMove 0.95, 0.95;
        Player.WeaponSlot 1, "RFBrowning";
        Player.WeaponSlot 2, "RFFAL";
        Player.ColorRange 0, 0;
        Player.AirCapacity 1.0;
    }

    override void PlayerThink()
    {
        let dev = RFDevHandler(StaticEventHandler.Find('RFDevHandler'));
        if (dev != null && dev.autopilot) dev.DriveAutopilot(self);
        Super.PlayerThink();
    }

    States
    {
    Spawn:
        TNT1 A -1;
        Loop;
    See:
        TNT1 A 4;
        Loop;
    Missile:
        TNT1 A 6;
        Goto Spawn;
    Melee:
        TNT1 A 6;
        Goto Spawn;
    Pain:
        TNT1 A 4 A_Pain;
        Goto Spawn;
    Death:
        TNT1 A 1 A_PlayerScream;
        TNT1 A 1 A_NoBlocking;
        TNT1 A -1;
        Stop;
    XDeath:
        Goto Death;
    }
}
