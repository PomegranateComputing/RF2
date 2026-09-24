// First-person weapons of RF01: Browning Hi-Power (wake-up weapon) and FN FAL (hero weapon).
// Frame letters follow the final-family manifests recovered from legacy/import.

// Impact resolves the struck surface family from the RF01 material prefixes.
class RFBulletPuff : Actor
{
    Default
    {
        +NOBLOCKMAP
        +NOGRAVITY
        +PUFFONACTORS
        +HITTRACER
        +ALLOWPARTICLES
        Radius 1;
        Height 1;
        Mass 5;
    }

    // 0 none, 1 mineral (plaster/stone/tile), 2 wood, 3 metal, 4 body
    int SurfaceMaterial()
    {
        if (tracer != null && tracer.bIsMonster) return 4;
        if (tracer != null) return 0;
        FLineTraceData hit;
        int flags = TRF_ABSPOSITION | TRF_THRUACTORS | TRF_NOSKY;
        bool found = LineTrace(angle + 180, 12, 0, flags, 0, 0, 0, hit);
        if (!found) found = LineTrace(angle, 12, 90, flags, 0, 0, 0, hit);
        if (!found) found = LineTrace(angle, 12, -90, flags, 0, 0, 0, hit);
        if (!found) return 0;
        String material = TexMan.GetName(hit.HitTexture);
        if (material.Left(3) == "RFW" || material.Left(3) == "RFD") return 2;
        if (material.Left(3) == "RFM") return 3;
        if (material.Left(2) == "RF") return 1;
        return 1;
    }

    override void PostBeginPlay()
    {
        Super.PostBeginPlay();
        int material = SurfaceMaterial();
        bool body = material == 4;
        Color grit = body ? 0x762d28 : material == 2 ? 0x795137 : material == 3 ? 0xc7c4ad : 0xc1b39a;
        Color haze = body ? 0x713932 : material == 2 ? 0x635044 : 0xa39d90;
        if (body) A_StartSound("rf/impact/flesh", CHAN_BODY, 0, 0.65);
        else if (material == 1) A_StartSound("rf/impact/plaster", CHAN_BODY, 0, 0.6);
        else if (material == 2) A_StartSound("rf/impact/wood", CHAN_BODY, 0, 0.6);
        else if (material == 3) A_StartSound("rf/impact/metal", CHAN_BODY, 0, 0.6);
        if (material == 0) return;
        for (int i = 0; i < 8; i++)
        {
            double spread = i * 45.0;
            A_SpawnParticle(grit, SPF_RELVEL, 12 + i % 4, body ? 1.3 : 1.7,
                0, 0, 0, 0, 0.5 + (i % 3) * 0.18, cos(spread) * 0.8,
                0.3 + sin(spread) * 0.7, 0, 0, -0.055, 0.95, -1, -0.035);
        }
        for (int i = 0; i < (material == 3 ? 0 : 5); i++)
        {
            double spread = i * 72.0;
            A_SpawnParticle(haze, SPF_RELVEL, 15 + i, body ? 1.8 : 3.0,
                0, 0, 0, 0, 0.16, cos(spread) * 0.2,
                0.1 + sin(spread) * 0.12, 0, 0, 0.01, 0.36, -1, 0.1);
        }
    }

    States
    {
    Spawn:
        TNT1 A 20;
        Stop;
    }
}

class RFBrowning : Weapon
{
    Default
    {
        Weapon.AmmoType "RFPistolAmmo";
        Weapon.AmmoUse 1;
        Weapon.AmmoGive 12;
        Weapon.SlotNumber 1;
        Weapon.SelectionOrder 2000;
        Weapon.BobStyle "InverseSmooth";
        Weapon.BobRangeX 0.6;
        Weapon.BobRangeY 0.4;
        Inventory.PickupMessage "$RF_PICKUP_BROWNING";
        Inventory.PickupSound "rf/item/pickup";
        Tag "$RF_WEAPON_BROWNING";
        +WEAPON.AMMO_OPTIONAL
        +WEAPON.NOAUTOFIRE
    }

    States
    {
    Ready:
        BHPG A 1
        {
            // Slide locked to the rear while the 9 mm reserve is empty.
            if (invoker.Owner != null && invoker.Owner.CountInv("RFPistolAmmo") <= 0)
            {
                let psp = player.FindPSprite(PSP_WEAPON);
                if (psp != null) psp.frame = 6;
            }
            A_WeaponReady();
        }
        Loop;
    Deselect:
        BHPG A 1 A_Lower(12);
        Loop;
    Select:
        BHPG A 1 A_Raise(12);
        Loop;
    Fire:
        BHPG A 0
        {
            if (invoker.Owner == null || invoker.Owner.CountInv("RFPistolAmmo") <= 0)
                return ResolveState("DryFire");
            return ResolveState("FireLoaded");
        }
    FireLoaded:
        BHPG B 2 Bright
        {
            A_StartSound("rf/browning/fire", CHAN_WEAPON);
            A_GunFlash();
            A_FireBullets(1.0, 0.6, 1, 18, "RFBulletPuff", FBF_USEAMMO | FBF_NORANDOM);
            A_WeaponOffset(-1, 34);
        }
        BHPG C 1 A_WeaponOffset(-2, 37);
        BHPG D 2
        {
            A_WeaponOffset(-3, 40);
            A_StartSound("rf/browning/slide", CHAN_ITEM, 0, 0.45);
            if (invoker.Owner != null) invoker.Owner.A_SpawnParticle(0xd0a45b, SPF_RELVEL, 12, 1.25,
                14, -8, 4, 0, 0.08, 0.22, 0.12, 0, 0, -0.055, 0.9, -1, 0.06);
        }
        BHPG E 2 A_WeaponOffset(-1, 35);
        BHPG F 3 A_WeaponOffset(0, 32);
        Goto Ready;
    DryFire:
        BHPG G 6 A_StartSound("rf/browning/dry", CHAN_ITEM);
        Goto Ready;
    Flash:
        TNT1 A 2 A_Light1;
        TNT1 A 0 A_Light0;
        Stop;
    Spawn:
        PIST A -1;
        Stop;
    }
}

class RFFAL : Weapon
{
    // The magazine is the only loaded-ammunition value; the reserve stays in RFRifleAmmo.
    int Magazine;
    bool Reloading;
    bool ReloadEmpty;
    const MagSize = 20;

    Default
    {
        Weapon.AmmoType "RFRifleAmmo";
        Weapon.AmmoUse 0;
        Weapon.AmmoGive 20;
        Weapon.SlotNumber 2;
        Weapon.SelectionOrder 700;
        Weapon.UpSound "rf/fal/raise";
        Weapon.BobStyle "InverseSmooth";
        Weapon.BobRangeX 0.5;
        Weapon.BobRangeY 0.35;
        Inventory.PickupMessage "$RF_PICKUP_FAL";
        Inventory.PickupSound "rf/item/pickup";
        Tag "$RF_WEAPON_FAL";
        +WEAPON.AMMO_OPTIONAL
        +WEAPON.NOAUTOFIRE
    }

    override void BeginPlay()
    {
        Super.BeginPlay();
        Magazine = MagSize;
    }

    clearscope int ReserveCount() const
    {
        if (Owner == null) return 0;
        let reserve = Owner.FindInventory("RFRifleAmmo");
        return reserve == null ? 0 : reserve.Amount;
    }

    bool CanReload() const
    {
        return Owner != null && Owner.health > 0 && !Reloading && Magazine < MagSize && ReserveCount() > 0;
    }

    // The single ammunition commit point of the reload choreography.
    void CommitReload()
    {
        if (Owner == null) return;
        int transfer = min(MagSize - Magazine, ReserveCount());
        if (transfer > 0 && Owner.TakeInventory("RFRifleAmmo", transfer, true)) Magazine += transfer;
    }

    override void OnDeselect(bool fromPowerup, bool onToss)
    {
        Super.OnDeselect(fromPowerup, onToss);
        Reloading = false;
        if (Owner != null) Owner.A_StopSound(CHAN_ITEM);
    }

    States
    {
    Ready:
        RFLV A 1 A_WeaponReady(WRF_ALLOWRELOAD);
        Loop;
    Deselect:
        RFLV A 1 A_Lower(12);
        Loop;
    Select:
        RFLV A 1 A_Raise(12);
        Loop;
    Fire:
        RFLV A 0
        {
            if (invoker.Magazine <= 0) return ResolveState("DryFire");
            invoker.Magazine--;
            return ResolveState("FireLoaded");
        }
    FireLoaded:
        RFLV B 2 Bright
        {
            A_StartSound("rf/fal/shot", CHAN_WEAPON);
            A_GunFlash();
            A_WeaponOffset(1, 35);
            A_FireBullets(1.2, 0.7, 1, 30, "RFBulletPuff", FBF_NORANDOM);
        }
        RFLV C 2
        {
            A_WeaponOffset(2, 39);
            A_StartSound("rf/fal/shell", CHAN_ITEM, 0, 0.5);
            if (invoker.Owner != null) invoker.Owner.A_SpawnParticle(0xc9b982, SPF_RELVEL, 16, 1.35,
                18, -10, 5, 0, 0.1, 0.28, 0.14, 0, 0, -0.06, 0.95, -1, 0.07);
        }
        RFLV D 2 A_WeaponOffset(1, 35);
        RFLV A 1 A_WeaponOffset(0, 32);
        Goto Ready;
    DryFire:
        RFLV A 6 A_StartSound("rf/fal/dry", CHAN_ITEM);
        Goto Ready;
    Reload:
        RFLV A 0
        {
            if (!invoker.CanReload()) return ResolveState("Ready");
            invoker.Reloading = true;
            invoker.ReloadEmpty = invoker.Magazine == 0;
            if (invoker.ReloadEmpty) return ResolveState("ReloadEmpty");
            return ResolveState("ReloadPartial");
        }
    ReloadPartial:
        RFLV E 4 { A_StartSound("rf/fal/cloth", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV F 4 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV G 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV H 3 { A_StartSound("rf/fal/latch", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV I 3 { A_StartSound("rf/fal/mag_out", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV J 4 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV K 4 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV L 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV M 3 { A_StartSound("rf/fal/mag_in", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV N 3 { A_StartSound("rf/fal/seat", CHAN_ITEM); invoker.CommitReload(); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV O 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV S 3 { A_StartSound("rf/fal/cloth", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV T 1 { invoker.Reloading = false; A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        Goto Ready;
    ReloadEmpty:
        RFLV E 4 { A_StartSound("rf/fal/cloth", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV F 4 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV G 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV H 3 { A_StartSound("rf/fal/latch", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV I 3 { A_StartSound("rf/fal/mag_out", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV J 4 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV K 4 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV L 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV M 3 { A_StartSound("rf/fal/mag_in", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV N 3 { A_StartSound("rf/fal/seat", CHAN_ITEM); invoker.CommitReload(); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV O 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV P 3 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV Q 3 { A_StartSound("rf/fal/action", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV R 2 A_WeaponReady(WRF_NOFIRE | WRF_NOBOB);
        RFLV S 3 { A_StartSound("rf/fal/cloth", CHAN_ITEM); A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        RFLV T 1 { invoker.Reloading = false; A_WeaponReady(WRF_NOFIRE | WRF_NOBOB); }
        Goto Ready;
    Flash:
        RFMZ A 2 Bright A_Light2;
        TNT1 A 0 A_Light0;
        Stop;
    Spawn:
        MGUN A -1;
        Stop;
    }
}
