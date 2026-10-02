// RF2 - the bench of the enemy families (outside the campaign; bench/familles/famille_map.py, map FAM01).
// One family at a time, any class: the three in the game, or a new one named by rf_banc_classe. Six stations run
// together and repeat: rotations, walk, obstacles, attack, pain, death and body. Each measure is printed
// (RF_BANC ...) and shown on screen: the poses as the actor plays them, "F10,G4,H14" = pose F ten tics, G four,
// H fourteen. New images must leave these lines unchanged (bench/familles/test_family_bench.py compares them).

// The post the specimen of the attack station strikes: it takes every blow and counts it.
class RFBenchDummy : Actor
{
    int hits;

    Default
    {
        Health 1000000;
        Radius 16;
        Height 56;
        Mass 100000;
        Scale 0.25;
        +SHOOTABLE
        +SOLID
        +NOBLOOD
        +DONTTHRUST
    }

    override int DamageMobj(Actor inflictor, Actor source, int damage, Name mod, int flags, double angle)
    {
        hits++;
        return 0;
    }

    States
    {
    Spawn:
        RFBD A -1;
        Stop;
    }
}

// The poses of an actor as it plays them: frame letter and tics, one run per pose.
class RFPoseRun play
{
    String runs;
    int curFrame, curTics;
    SpriteID curSprite;

    void Reset()
    {
        runs = "";
        curTics = 0;
        curFrame = -1;
    }

    void Feed(Actor a)
    {
        if (a.frame != curFrame || a.sprite != curSprite)
        {
            Flush();
            curFrame = a.frame;
            curSprite = a.sprite;
        }
        curTics++;
    }

    void Flush()
    {
        if (curTics > 0) runs = String.Format("%s%s%c%d", runs, runs.Length() > 0 ? "," : "", 65 + curFrame, curTics);
        curTics = 0;
    }
}

class RFFamilyBench : EventHandler
{
    const SPOT_VIEW = 9100;
    const SPOT_WALK = 9200;
    const PP_WALK = 9211;
    const SPOT_RUN = 9300;
    const PP_RUN = 9311;
    const SPOT_STRIKE = 9400;
    const SPOT_DUMMY = 9401;
    const SPOT_PAIN = 9500;
    const SPOT_DEATH = 9600;
    const TID_WALK = 9250;
    const TID_RUN = 9350;
    const GATES = 5;
    const GATE_TIMEOUT = 35 * 18;

    bool active;
    class<Actor> kind;
    String kindName;
    Array<Actor> ring;                // 8 standing specimens, then 8 that play the poses
    Array<State> seq;                 // the poses played by the far arc: walk, attack, pain
    int seqAt, seqLeft;
    Actor walker, runner, striker, sufferer, mortal;
    RFBenchDummy dummy;
    RFPoseRun atkRun, painRun, deathRun;

    Actor walkGoal;
    int walkLegStart, walkLegs, walkSteps;
    double walkDist;
    Vector2 walkPrev;
    String walkLine;
    Actor runGoal;
    int runGate, runGateTic, runRespawn, runTries;
    String runLine;
    bool attacking;
    int atkStart, atkHits, atkImpact, atkShot, atkCount, strikeRespawn;
    State atkPrev;
    String atkFrom, atkLine;
    bool hurting;
    int painNext, painCount;
    String painLine;
    bool dying;
    int deathNext, deathCount, deathClear;
    String deathLine;
    bool reported;

    static Actor Spot(int tid)
    {
        let it = Level.CreateActorIterator(tid);
        return it.Next();
    }

    Actor Specimen(Vector3 where, double ang)
    {
        let mo = Actor.Spawn(kind, where, ALLOW_REPLACE);
        if (mo != null)
        {
            mo.angle = ang;
            mo.SetZ(mo.floorz);
        }
        return mo;
    }

    Actor SpecimenAt(int tid)
    {
        let s = Spot(tid);
        return s != null ? Specimen(s.Pos, s.angle) : null;
    }

    static bool InSeq(Actor a, StateLabel label)
    {
        State s = a.ResolveState(label);
        return s != null && a.InStateSequence(a.CurState, s);
    }

    static bool Resting(Actor a)
    {
        return InSeq(a, "See") || InSeq(a, "Spawn");
    }

    // The states of a label, in order, until the sequence ends or comes back on itself.
    void AddSeq(Actor ref, StateLabel label, int loops)
    {
        State first = ref.ResolveState(label);
        if (first == null) return;
        for (int n = 0; n < loops; n++)
        {
            Array<State> seen;
            State s = first;
            while (s != null && s.Tics > 0 && seen.Find(s) == seen.Size() && seen.Size() < 24)
            {
                seen.Push(s);
                seq.Push(s);
                State nx = s.NextState;
                if (nx == null || !ref.InStateSequence(nx, first)) break;
                s = nx;
            }
        }
    }

    void Clear()
    {
        for (int i = 0; i < ring.Size(); i++) if (ring[i] != null) ring[i].Destroy();
        ring.Clear();
        seq.Clear();
        if (walker != null) walker.Destroy();
        if (runner != null) runner.Destroy();
        if (striker != null) striker.Destroy();
        if (sufferer != null) sufferer.Destroy();
        if (mortal != null) mortal.Destroy();
        let it = ThinkerIterator.Create('Actor');
        Actor a;
        while ((a = Actor(it.Next())) != null) if (a.bMissile) a.Destroy();
    }

    void SendOn(Actor mo, int tid, int goal)
    {
        if (mo == null) return;
        mo.ChangeTid(tid);
        Level.ExecuteSpecial(229, null, null, false, tid, goal, 0, 1);       // Thing_SetGoal: patrol, never distracted
    }

    void Setup(class<Actor> k)
    {
        Clear();
        kind = k;
        kindName = k.GetClassName();
        let def = GetDefaultByType(k);
        Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC CLASSE nom=%s rayon=%.0f hauteur=%.0f vitesse=%.0f sante=%d echelle=%.2f portee_melee=%.0f",
                       kindName, def.radius, def.height, def.Speed, def.health, def.Scale.X, def.MeleeRange);
        // the two arcs of the rotations, about the view mark
        let view = Spot(SPOT_VIEW);
        for (int row = 0; row < 2; row++)
        {
            for (int i = 0; i < 8; i++)
            {
                double a = 55 + i * 10;
                double r = row == 0 ? 360 : 470;
                let mo = Specimen((view.Pos.X + r * cos(a), view.Pos.Y + r * sin(a), 0), a + 180 + 45 * i);
                if (mo != null) mo.Deactivate(null);
                ring.Push(mo);
            }
        }
        if (ring[0] != null)
        {
            AddSeq(ring[0], "See", 3);
            AddSeq(ring[0], "Melee", 1);
            if (ring[0].ResolveState("Missile") != ring[0].ResolveState("Melee")) AddSeq(ring[0], "Missile", 1);
            AddSeq(ring[0], "Pain", 2);
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC MARCHE_POSES classe=%s poses=%s", kindName, Poses("See"));
        }
        seqAt = -1;
        seqLeft = 0;
        walker = SpecimenAt(SPOT_WALK);
        SendOn(walker, TID_WALK, PP_WALK + 1);
        walkGoal = null;
        walkLegs = 0;
        walkLine = "";
        SpawnRunner();
        runLine = "";
        dummy = RFBenchDummy(Spot(SPOT_DUMMY + 10000));
        if (dummy == null)
        {
            let s = Spot(SPOT_DUMMY);
            dummy = RFBenchDummy(Actor.Spawn('RFBenchDummy', s.Pos));
            dummy.angle = s.angle;
            dummy.ChangeTid(SPOT_DUMMY + 10000);
        }
        SpawnStriker();
        atkCount = 0;
        atkLine = "";
        sufferer = SpecimenAt(SPOT_PAIN);
        hurting = false;
        painNext = Level.maptime + 105;
        painCount = 0;
        painLine = "";
        mortal = SpecimenAt(SPOT_DEATH);
        dying = false;
        deathNext = Level.maptime + 140;
        deathClear = 0;
        deathCount = 0;
        deathLine = "";
        reported = false;
    }

    // The poses of a label as written in the class: "B4,C4,D4,E4".
    String Poses(StateLabel label)
    {
        String res = "";
        if (ring.Size() == 0 || ring[0] == null) return res;
        State first = ring[0].ResolveState(label);
        Array<State> seen;
        State s = first;
        while (s != null && s.Tics > 0 && seen.Find(s) == seen.Size() && seen.Size() < 24)
        {
            seen.Push(s);
            res = String.Format("%s%s%c%d", res, res.Length() > 0 ? "," : "", 65 + s.Frame, s.Tics);
            State nx = s.NextState;
            if (nx == null || !ring[0].InStateSequence(nx, first)) break;
            s = nx;
        }
        return res;
    }

    void SpawnRunner()
    {
        runner = SpecimenAt(SPOT_RUN);
        SendOn(runner, TID_RUN, PP_RUN);
        runGoal = runner != null ? runner.goal : null;
        runGate = 0;
        runGateTic = Level.maptime;
        runRespawn = 0;
    }

    void SpawnStriker()
    {
        striker = SpecimenAt(SPOT_STRIKE);
        attacking = false;
        atkPrev = null;
        strikeRespawn = 0;
        if (striker != null && dummy != null)
        {
            striker.target = dummy;
            striker.SetState(striker.SeeState);
        }
    }

    static String GateName(int g)
    {
        static const String names[] = { "pilier", "marche de 24", "porte de 96", "porte de 64", "porte de 48" };
        return g >= 0 && g < GATES ? names[g] : "?";
    }

    override void WorldLoaded(WorldEvent e)
    {
        active = Level.MapName ~== "FAM01";
        if (!active) return;
        atkRun = new("RFPoseRun");
        painRun = new("RFPoseRun");
        deathRun = new("RFPoseRun");
    }

    override void WorldLineActivated(WorldEvent e)
    {
        if (!active || e.ActivatedLine == null || e.Thing == null || e.Thing.player == null) return;
        static const String classes[] = { "RFOrderly", "RFBrancardier", "RFPorteRegistre" };
        int n = e.ActivatedLine.GetUDMFInt('user_scene');
        if (n < 1 || n > 3) return;
        class<Actor> k = (class<Actor>)(classes[n - 1]);
        if (k != null && k != kind) Setup(k);
    }

    void TickRing()
    {
        if (seq.Size() == 0 || --seqLeft > 0) return;
        seqAt = (seqAt + 1) % seq.Size();
        seqLeft = seq[seqAt].Tics;
        for (int i = 8; i < ring.Size(); i++)
        {
            if (ring[i] == null) continue;
            ring[i].sprite = seq[seqAt].sprite;
            ring[i].frame = seq[seqAt].Frame;
        }
    }

    // The walk between two patrol points: the length of a step (one move of the walk cycle), how often one is made,
    // and the speed over the leg. Turning round at each end is part of the leg.
    void TickWalker()
    {
        if (walker == null || walker.health <= 0) return;
        double moved = (walker.Pos.XY - walkPrev).Length();
        walkPrev = walker.Pos.XY;
        if (moved > 0.01 && moved < 64) { walkSteps++; walkDist += moved; }
        if (walker.goal == walkGoal) return;
        // the goal changed: a patrol point was reached
        if (walkGoal != null && walker.goal != null && walkLegs++ > 0 && walkSteps > 0)
        {
            int tics = Level.maptime - walkLegStart;
            double step = walkDist / walkSteps;
            walkLine = String.Format("pas de %.1f u, un tous les %.1f tics, %.2f u/tic", step, double(tics) / walkSteps, walkDist / max(tics, 1));
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC MARCHE classe=%s pas=%.1f cadence=%.1f vitesse=%.2f distance=%d tics=%d", kindName, step,
                             double(tics) / walkSteps, walkDist / max(tics, 1), int(walkDist), tics);
        }
        walkGoal = walker.goal;
        walkLegStart = Level.maptime;
        walkSteps = 0;
        walkDist = 0;
    }

    void TickRunner()
    {
        if (runRespawn > 0)
        {
            if (Level.maptime >= runRespawn)
            {
                if (runner != null) runner.Destroy();
                SpawnRunner();
            }
            return;
        }
        if (runner == null || runner.health <= 0) return;
        if (runner.goal != runGoal)
        {
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC OBSTACLE classe=%s passe=%s tics=%d", kindName, GateName(runGate), Level.maptime - runGateTic);
            runGate++;
            runGateTic = Level.maptime;
            runGoal = runner.goal;
            if (runGate >= GATES)
            {
                runLine = "tout est franchi (pilier, marche de 24, portes de 96, 64 et 48)";
                Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC OBSTACLES classe=%s resultat=passe", kindName);
                runTries = 0;
                runRespawn = Level.maptime + 70;
            }
            return;
        }
        // a gate narrower than the body: no need to wait
        static const int widths[] = { 96, 9999, 96, 64, 48 };
        bool tooWide = runner.radius * 2 > widths[runGate];
        if (tooWide || Level.maptime - runGateTic > GATE_TIMEOUT)
        {
            if (!tooWide && ++runTries < 3)                                   // the walk has its share of chance: three tries
            {
                Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC OBSTACLE classe=%s essai=%d sans_franchir=%s", kindName, runTries, GateName(runGate));
                runRespawn = Level.maptime + 35;
                return;
            }
            runLine = tooWide ? String.Format("ne passe pas : %s (corps de %.0f u de large)", GateName(runGate), runner.radius * 2)
                              : String.Format("arrêté devant : %s, trois essais (corps de %.0f u de large)", GateName(runGate), runner.radius * 2);
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC OBSTACLES classe=%s resultat=%s devant=%s franchis=%d", kindName,
                             tooWide ? "trop_large" : "arrete", GateName(runGate), runGate);
            runTries = 0;
            runRespawn = Level.maptime + 70;
        }
    }

    void TickStriker()
    {
        if (strikeRespawn > 0)
        {
            if (Level.maptime >= strikeRespawn)
            {
                if (striker != null) striker.Destroy();
                SpawnStriker();
            }
            return;
        }
        if (striker == null || dummy == null || striker.health <= 0) return;
        if (striker.target != dummy) striker.target = dummy;
        if (Level.maptime % 70 == 0 && CVar.GetCVar('rf_dev_log').GetBool())
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC_DEV frappeur x=%.0f y=%.0f dist=%.0f cible=%s repos=%d vue=%d portee=%d",
                             striker.Pos.X, striker.Pos.Y, striker.Distance2D(dummy), striker.target.GetClassName(), Resting(striker),
                             striker.CheckSight(dummy), striker.CheckMeleeRange());
        State melee = striker.ResolveState("Melee"), missile = striker.ResolveState("Missile");
        bool m1 = melee != null && striker.CurState == melee, m2 = missile != null && striker.CurState == missile;
        bool begins = (m1 || m2) && striker.CurState != atkPrev;       // the first pose of an attack, just entered
        atkPrev = striker.CurState;
        // an attack ends when the specimen walks again, or starts the next one at once (a target within reach)
        if (attacking && (Resting(striker) || begins))
        {
            atkRun.Flush();
            attacking = false;
            atkCount++;
            atkLine = String.Format("%s : %s", atkFrom, atkRun.runs);
            if (atkShot >= 0) atkLine = String.Format("%s, tir à +%d", atkLine, atkShot);
            if (atkImpact >= 0) atkLine = String.Format("%s, coup à +%d", atkLine, atkImpact);
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC ATTAQUE classe=%s depart=%s poses=%s total=%d tir=%d coup=%d", kindName, atkFrom,
                             atkRun.runs, Level.maptime - atkStart, atkShot, atkImpact);
            if (atkCount % 6 == 0)                                          // back to its mark: the approach is seen again
            {
                strikeRespawn = Level.maptime + 35;
                return;
            }
        }
        if (!attacking)
        {
            if (!begins) return;
            attacking = true;
            atkFrom = m1 ? "Melee" : "Missile";
            atkStart = Level.maptime;
            atkHits = dummy.hits;
            atkImpact = -1;
            atkShot = -1;
            atkRun.Reset();
        }
        atkRun.Feed(striker);
        if (atkImpact < 0 && dummy.hits != atkHits) atkImpact = Level.maptime - atkStart;
        if (atkShot < 0)
        {
            let it = ThinkerIterator.Create('Actor');
            Actor a;
            while ((a = Actor(it.Next())) != null)
            {
                if (a.bMissile && a.target == striker) { atkShot = Level.maptime - atkStart; break; }
            }
        }
    }

    void TickSufferer()
    {
        if (sufferer == null || sufferer.health <= 0) return;
        if (!hurting)
        {
            if (Level.maptime < painNext || !Resting(sufferer)) return;
            int chance = sufferer.PainChance;
            sufferer.PainChance = 256;
            sufferer.DamageMobj(null, null, 1, 'None');
            sufferer.PainChance = chance;
            sufferer.health = sufferer.SpawnHealth();
            painNext = Level.maptime + 140;
            if (Resting(sufferer)) return;                                   // no pain state
            hurting = true;
            painRun.Reset();
        }
        if (Resting(sufferer))
        {
            painRun.Flush();
            hurting = false;
            painCount++;
            painLine = painRun.runs;
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC DOULEUR classe=%s poses=%s", kindName, painRun.runs);
            return;
        }
        painRun.Feed(sufferer);
    }

    void TickMortal()
    {
        if (deathClear > 0)
        {
            if (Level.maptime >= deathClear)
            {
                if (mortal != null) mortal.Destroy();
                mortal = SpecimenAt(SPOT_DEATH);
                deathClear = 0;
                deathNext = Level.maptime + 140;
            }
            return;
        }
        if (!dying)
        {
            if (mortal == null || Level.maptime < deathNext) return;
            mortal.DamageMobj(null, null, mortal.health + 100, 'None', DMG_FORCED);
            dying = true;
            deathRun.Reset();
        }
        if (mortal == null)
        {
            dying = false;
            deathLine = String.Format("%s, puis aucun corps (acteur retiré)", deathRun.runs);
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC MORT classe=%s poses=%s corps=aucun", kindName, deathRun.runs);
            deathCount++;
            deathClear = Level.maptime + 70;
            return;
        }
        if (mortal.CurState != null && mortal.CurState.Tics == -1)
        {
            deathRun.Flush();
            dying = false;
            String tex = TexMan.GetName(mortal.CurState.GetSpriteTexture(0));
            deathLine = String.Format("%s, corps : %s", deathRun.runs, tex);
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC MORT classe=%s poses=%s corps=%s solide=%d rayon=%.0f hauteur=%.0f", kindName, deathRun.runs, tex,
                           mortal.bSolid, mortal.radius, mortal.height);
            deathCount++;
            deathClear = Level.maptime + 210;                                 // the body stays six seconds
            return;
        }
        deathRun.Feed(mortal);
    }

    override void WorldTick()
    {
        if (!active || !playeringame[0] || players[0].mo == null) return;
        players[0].cheats |= CF_NOTARGET | CF_GODMODE;                        // an observer: nothing here hunts him
        if (kind == null)
        {
            if (Level.maptime < 2) return;
            class<Actor> k = (class<Actor>)(CVar.FindCVar('rf_banc_classe').GetString());
            if (k == null)
            {
                Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC CLASSE inconnue : %s (RFOrderly a sa place)", CVar.FindCVar('rf_banc_classe').GetString());
                k = 'RFOrderly';
            }
            Setup(k);
        }
        TickRing();
        TickWalker();
        TickRunner();
        TickStriker();
        TickSufferer();
        TickMortal();
        if (!reported && atkCount >= 3 && painCount >= 2 && deathCount >= 1 && walkLine.Length() > 0 && runLine.Length() > 0)
        {
            reported = true;
            Console.PrintfEx(PRINT_HIGH | PRINT_NONOTIFY, "RF_BANC BILAN classe=%s t=%d", kindName, Level.maptime);
        }
    }

    ui void Line(int row, String text)
    {
        Font f = NewSmallFont;
        Screen.DrawText(f, row == 0 ? Font.CR_GOLD : Font.CR_WHITE, 6, 6 + row * (f.GetHeight() + 2), text,
                        DTA_VirtualWidth, 960, DTA_VirtualHeight, 540, DTA_KeepRatio, true);
    }

    override void RenderOverlay(RenderEvent e)
    {
        if (!active) return;
        Line(0, String.Format("BANC DES FAMILLES : %s   (dalles de bois au sud : 1 infirmier, 2 brancardier, 3 porte-registre)", kindName));
        Line(1, "rotations : deux arcs au nord de la dalle centrale (debout, puis marche, attaque et douleur dans les huit vues)");
        Line(2, String.Format("marche (ouest) : %s", walkLine));
        Line(3, String.Format("obstacles (est) : %s", runLine));
        Line(4, String.Format("attaque (nord-est) : %s", atkLine));
        Line(5, String.Format("douleur (nord-ouest) : %s", painLine));
        Line(6, String.Format("mort et corps (nord-ouest) : %s", deathLine));
    }
}
