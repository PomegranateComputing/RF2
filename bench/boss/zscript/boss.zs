// RF2 boss bench (01/10/2026): first boss prototype, OUTSIDE the campaign. Loaded over a frozen game build by
// bench/boss/build_boss_bench.py; no campaign map, inventory or class is changed.
//
// LE SURVEILLANT-CHEF (bench/boss/FICHE_BOSS_SURVEILLANT.md): a DECLARED ADAPTATION, not a character of the novel. He
// heads the staff of Sainte-Anne who carry on their procedure behind Viktor (accepted adaptation of RF01-RF05): the
// orderlies, the stretcher-bearers, the register-bearers answer to him. His threat is the procedure itself: the
// register, the stamp, the whistle that calls the staff. Never a patient, never an illness, never a figure of the text.
//
// Attacks, each announced (sound and pose before the blow, so that it can be read and avoided):
//   Tampon (stamp)   close: he inks the stamp, raises it (24 tics), slams it on the floor: a shock along the floor,
//                    128 u round him; step back or jump the timing.
//   Registres        at range: he opens the ledger (18 tics), throws three bound registers in a fan (lobbed).
//   Sifflet          he blows the whistle (30 tics): two orderlies come in by the side doors (three times at most).
// Phase 2 below half health: he throws his cap down, walks faster, whistles at once, stamps twice in a row.

// A point of the bench (start, middle of the hall, the staff's doors, the player's return): invisible.
class RFBossSpot : Actor
{
    Default { +NOGRAVITY; +NOBLOCKMAP; +NOINTERACTION; RenderStyle "None"; }
    States { Spawn: TNT1 A -1; Stop; }
}

class RFBossLedger : Actor
{
    Default
    {
        Radius 6;
        Height 8;
        Speed 15;
        Damage 9;
        Gravity 0.45;
        Projectile;
        -NOGRAVITY
        +DROPOFF
        Scale 0.3;
        SeeSound "rf/boss/throw";
        DeathSound "rf/boss/ledger_hit";
    }
    States
    {
    Spawn: BSLG A 3; BSLG B 3; Loop;
    Death: BSLG C 12; Stop;
    }
}

// The shock of the stamp along the floor: a ring that spreads and hurts what stands on the floor within it.
class RFBossStampWave : Actor
{
    Default { +NOGRAVITY; +NOBLOCKMAP; +NOINTERACTION; RenderStyle "Add"; Alpha 0.6; Scale 0.6; }
    int age;
    override void Tick()
    {
        Super.Tick();
        if (isFrozen()) return;
        age++;
        Scale = (0.6 + age * 0.12, 0.6 + age * 0.12);
        Alpha = max(0.0, 0.6 - age * 0.04);
        if (age >= 15) Destroy();
    }
    States { Spawn: BSWV A -1 Bright; Stop; }
}

class RFBossSurveillant : RFEnemy
{
    int phase;              // 1, then 2 below half health
    int summons;            // whistles used (three at most)
    int lastSummon;
    bool entering;
    Vector2 entryGoal;
    int announce;           // 0 none, 1 stamp, 2 registers, 3 whistle (read by the bench HUD)

    Default
    {
        Health 1200;
        Radius 24;
        Height 66;
        Mass 600;
        Speed 6;
        PainChance 24;
        MeleeRange 96;
        MaxTargetRange 900;
        MinMissileChance 140;
        Monster;
        +FLOORCLIP
        +BOSS
        +DONTMORPH
        +NOINFIGHTING
        Scale 0.38;
        SeeSound "rf/boss/whistle_short";
        PainSound "rf/boss/pain";
        DeathSound "rf/boss/death";
        Tag "$RF_BOSS_SURVEILLANT";
        Obituary "$RF_OBIT_BOSS";
    }

    // The entry: the doors open, he walks to the middle of the hall, untouchable, stamps the register: it begins.
    void BeginEntry(Actor by, Vector2 goal)
    {
        entering = true;
        phase = 1;
        entryGoal = goal;
        target = by;
        awaitingCue = false;
        bInvulnerable = true;
        SetStateLabel("Entry");
    }

    void EntryWalk()
    {
        Vector2 d = entryGoal - Pos.XY;
        double len = d.Length();
        if (len < 8) { SetStateLabel("EntryStamp"); return; }
        angle = VectorAngle(d.X, d.Y);
        TryMove(Pos.XY + d / len * min(Speed, len), true);
    }

    void EndEntry()
    {
        entering = false;
        bInvulnerable = false;
        if (target != null) A_FaceTarget();
    }

    // Decisions of the walk: the whistle when it is time, otherwise A_Chase (melee = stamp, missile = registers).
    void BossChase()
    {
        announce = 0;
        if (target != null && target.health > 0 && summons < 3
            && (phase == 2 ? Level.maptime - lastSummon > 35 * 14 : Level.maptime - lastSummon > 35 * 24)
            && CheckSight(target))
        {
            SetStateLabel("Whistle");
            return;
        }
        A_Chase();
    }

    void InkStamp()
    {
        announce = 1;
        A_FaceTarget();
        Vel.X = Vel.Y = 0;
        A_StartSound("rf/boss/ink", CHAN_VOICE, 0, 1.0);
    }

    void Stamp()
    {
        A_StartSound("rf/boss/stamp", CHAN_WEAPON, 0, 1.0, ATTN_NONE);
        Spawn("RFBossStampWave", Pos + (0, 0, 2));
        // The shock along the floor: what stands within 128 u and touches the floor is struck (not over a ledge).
        let it = BlockThingsIterator.Create(self, 136);
        while (it.Next())
        {
            Actor a = it.thing;
            if (a == self || a.health <= 0 || !a.bShootable || a is 'RFEnemy') continue;
            if (Distance2D(a) > 128 + a.radius || abs(a.Pos.Z - a.floorz) > 4 || abs(a.floorz - floorz) > 24) continue;
            a.DamageMobj(self, self, phase == 2 ? 22 : 16, 'Melee');
            a.Thrust(6, AngleTo(a));
        }
        A_QuakeEx(2, 2, 1, 12, 0, 400, "", QF_SCALEDOWN);
        announce = 0;
    }

    void OpenLedger()
    {
        announce = 2;
        A_FaceTarget();
        Vel.X = Vel.Y = 0;
        A_StartSound("rf/boss/ledger_open", CHAN_VOICE, 0, 1.0);
    }

    void ThrowLedgers()
    {
        if (target == null || target.health <= 0) return;
        A_FaceTarget();
        double pitch = LobPitch(target, 52);
        for (int k = -1; k <= 1; k++)
            A_SpawnProjectile("RFBossLedger", 52, 0, k * 9, CMF_AIMDIRECTION | CMF_ABSOLUTEPITCH, pitch);
        announce = 0;
    }

    double LobPitch(Actor t, double spawnHeight)
    {
        let b = GetDefaultByType('RFBossLedger');
        double v = b.Speed;
        double g = b.Gravity * Level.Gravity * CurSector.gravity * 0.00125;
        double d = max(Distance2D(t), 1);
        double h = (t.pos.z + t.height * 0.5) - (pos.z + spawnHeight);
        double a = g * d * d / (2 * v * v);
        double disc = d * d - 4 * a * (a + h);
        if (disc < 0) return -40;
        return -atan((d - sqrt(disc)) / (2 * a));
    }

    void BlowWhistle()
    {
        announce = 3;
        Vel.X = Vel.Y = 0;
        A_StartSound("rf/boss/whistle", CHAN_VOICE, 0, 1.0, ATTN_NONE);
    }

    void CallStaff()
    {
        summons++;
        lastSummon = Level.maptime;
        let bench = RFBossBench(EventHandler.Find('RFBossBench'));
        if (bench != null) bench.CallStaff(target);
        announce = 0;
    }

    override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
    {
        int r = Super.DamageMobj(inflictor, source, damage, mod, flags, angle);
        if (phase < 2 && health > 0 && health <= GetSpawnHealth() / 2)
        {
            phase = 2;
            Speed = 8;
            lastSummon = Level.maptime - 35 * 30;          // he whistles at once
            SetStateLabel("PhaseTwo");
        }
        return r;
    }

    States
    {
    Spawn:
        BSSV A 10 RFLook;
        Loop;
    Entry:
        BSSV BCDE 5 EntryWalk;
        Loop;
    EntryStamp:
        BSSV H 20 A_StartSound("rf/boss/ledger_open", CHAN_VOICE);
        BSSV F 14 A_StartSound("rf/boss/ink", CHAN_VOICE);
        BSSV G 10 A_StartSound("rf/boss/stamp", CHAN_WEAPON, 0, 1.0, ATTN_NONE);
        BSSV A 10 EndEntry;
        Goto See;
    See:
        BSSV B 5 BossChase;
        BSSV C 5 { BossChase(); A_StartSound("rf/boss/step", CHAN_BODY, 0, 0.6); }
        BSSV D 5 BossChase;
        BSSV E 5 { BossChase(); A_StartSound("rf/boss/step", CHAN_BODY, 0, 0.6); }
        Loop;
    Melee:
        BSSV F 24 InkStamp;
        BSSV G 6 Stamp;
        BSSV G 12 A_JumpIf(phase == 2 && random(0, 1) == 0, "Melee2");
        Goto See;
    Melee2:
        BSSV F 14 InkStamp;
        BSSV G 6 Stamp;
        BSSV G 12;
        Goto See;
    Missile:
        BSSV H 18 OpenLedger;
        BSSV I 6 ThrowLedgers;
        BSSV I 10;
        Goto See;
    Whistle:
        BSSV J 30 BlowWhistle;
        BSSV J 6 CallStaff;
        Goto See;
    PhaseTwo:
        BSSV K 20 A_StartSound("rf/boss/pain", CHAN_VOICE, 0, 1.0, ATTN_NONE);
        BSSV A 10;
        Goto See;
    Pain:
        BSSV K 6 A_Pain;
        Goto See;
    Death:
        BSSV L 8 { BeginDeath(); A_Scream(); announce = 0; }
        BSSV M 8 A_NoBlocking;
        BSSV N 10 A_StartSound("rf/world/body_fall", CHAN_BODY, 0, 1.0);
        BSSV O -1;
        Stop;
    }
}

// The bench: the hall of the porters' lodge. Crossing the line of the hall starts the entry; the bench HUD shows
// the bar and the announced attack (a test aid); after the victory, "Utiliser" or 6 s starts it again (reprise).
class RFBossBench : EventHandler
{
    const ENTRY_LINE = 901;       // user_scene of the hall's entry line
    const SIDE_DOORS = 902;       // tag of the side doors the staff come through
    const BOSS_DOOR = 900;        // tag of the north doors he comes through
    const SPOT_START = 910;       // tid: the boss's start (behind the north doors)
    const SPOT_GOAL = 911;        // tid: the middle of the hall
    const SPOT_STAFF = 912;       // tid: where the called staff come in
    const SPOT_PLAYER = 913;      // tid: the player's return point for the reprise

    bool active, engaged, won;
    int wonTic, attempts, victories;
    RFBossSurveillant boss;

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "BOSS01";
        if (!active || e.IsSaveGame) return;
        boss = RFBossSurveillant(ThinkerIterator.Create('RFBossSurveillant').Next());
    }

    Actor Spot(int tid)
    {
        let it = Level.CreateActorIterator(tid);
        return it.Next();
    }

    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || engaged || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        if (e.ActivatedLine.GetUDMFInt('user_scene') != ENTRY_LINE) return;
        StartFight(e.Thing);
    }

    void StartFight(Actor pl)
    {
        if (boss == null || boss.health <= 0) return;
        engaged = true;
        attempts++;
        Level.MakeAutoSave();                                  // death resumes here (the game's death screen)
        Level.ExecuteSpecial(11, pl, null, false, BOSS_DOOR, 32);          // Door_Open
        Actor goal = Spot(SPOT_GOAL);
        boss.BeginEntry(pl, goal != null ? goal.Pos.XY : pl.Pos.XY);
        Console.Printf("RF_BOSS entry attempt=%d t=%d", attempts, Level.maptime);
    }

    void CallStaff(Actor target)
    {
        Level.ExecuteSpecial(11, target, null, false, SIDE_DOORS, 64);
        let it = Level.CreateActorIterator(SPOT_STAFF);
        Actor s;
        int n = 0;
        while ((s = it.Next()) != null && n < 2)
        {
            let o = Actor.Spawn('RFOrderly', s.Pos, ALLOW_REPLACE);
            if (o != null)
            {
                o.target = target;
                o.SetStateLabel("See");
                n++;
            }
        }
        Console.Printf("RF_BOSS whistle staff=%d t=%d", n, Level.maptime);
    }

    override void WorldThingDied(WorldEvent e)
    {
        if (!active || e.Thing == null || e.Thing != boss) return;
        won = true;
        wonTic = Level.maptime;
        victories++;
        Console.Printf("RF_BOSS victory t=%d attempts=%d", Level.maptime, attempts);
    }

    override void WorldTick()
    {
        if (!active || !won || !playeringame[0]) return;
        Actor pl = players[0].mo;
        if (pl == null) return;
        bool use = (players[0].cmd.buttons & BT_USE) != 0;
        if (Level.maptime - wonTic < 35 * 2 || (Level.maptime - wonTic < 35 * 8 && !use)) return;
        Reprise(pl);
    }

    // The reprise: the hall as it was, the boss back behind his doors, the player at the hall's door, healed, armed.
    void Reprise(Actor pl)
    {
        won = false;
        engaged = false;
        let it = ThinkerIterator.Create('RFOrderly');
        Actor o;
        while ((o = Actor(it.Next())) != null) o.Destroy();
        if (boss != null) boss.Destroy();
        Actor start = Spot(SPOT_START);
        if (start != null)
        {
            boss = RFBossSurveillant(Actor.Spawn('RFBossSurveillant', start.Pos));
            if (boss != null) { boss.angle = start.angle; boss.awaitingCue = true; }
        }
        Level.ExecuteSpecial(10, pl, null, false, BOSS_DOOR, 64);       // Door_Close: his doors shut again
        Level.ExecuteSpecial(10, pl, null, false, SIDE_DOORS, 64);
        Actor back = Spot(SPOT_PLAYER);
        if (back != null) { pl.SetOrigin(back.Pos, false); pl.angle = back.angle; }
        pl.GiveBody(100);
        pl.GiveInventory('RFRifleAmmo', 60);
        pl.GiveInventory('RFPistolAmmo', 36);
        Console.Printf("RF_BOSS reprise t=%d", Level.maptime);
    }

    override void RenderOverlay(RenderEvent e)
    {
        if (!active) return;
        Font f = Font.GetFont('RFText');
        if (f == null) f = SmallFont;
        double s = max(Screen.GetHeight() / 1080.0, 0.5);
        int sw = Screen.GetWidth();
        if (won)
        {
            String v = StringTable.Localize("$RF_BOSS_VICTORY");
            Screen.DrawText(f, Font.CR_WHITE, (sw - f.StringWidth(v) * 2 * s) / 2, Screen.GetHeight() * 0.38, v,
                            DTA_ScaleX, 2 * s, DTA_ScaleY, 2 * s);
            return;
        }
        if (!engaged || boss == null || boss.health <= 0) return;
        double w = 640 * s, h = 14 * s, x = (sw - w) / 2, y = 40 * s;
        double k = clamp(double(boss.health) / boss.GetSpawnHealth(), 0.0, 1.0);
        Screen.Dim(0, 0.6, int(x - 4 * s), int(y - 36 * s), int(w + 8 * s), int(h + 42 * s));
        Screen.Dim(Color(255, 70, 66, 60), 1.0, int(x), int(y), int(w), int(h));
        Screen.Dim(Color(255, 186, 40, 34), 1.0, int(x), int(y), int(w * k), int(h));
        String name = StringTable.Localize("$RF_BOSS_SURVEILLANT") .. (boss.phase == 2 ? "  II" : "");
        Screen.DrawText(f, Font.CR_WHITE, x, y - 30 * s, name, DTA_ScaleX, 1.6 * s, DTA_ScaleY, 1.6 * s);
        if (boss.announce > 0)
        {
            static const String KEYS[] = { "", "$RF_BOSS_A1", "$RF_BOSS_A2", "$RF_BOSS_A3" };
            String a = StringTable.Localize(KEYS[boss.announce]);
            Screen.DrawText(f, Font.CR_GOLD, x + w - f.StringWidth(a) * 1.6 * s, y - 30 * s, a, DTA_ScaleX, 1.6 * s, DTA_ScaleY, 1.6 * s);
        }
    }
}
