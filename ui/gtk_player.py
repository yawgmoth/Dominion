import gtk
import gobject
import threading
import sys
import base_player

class GtkPlayer(base_player.BasePlayer):
    def __init__(self, name):
        self.name = name
        window = gtk.Window()
        main_container = gtk.HPaned()
        
        action_vbox = gtk.VBox()
        self.question_label = gtk.Label("lalala")
        action_vbox.pack_start(self.question_label)
        answer_hbox = gtk.HBox()
        self.yes = gtk.Button(label="Yes")
        self.yes.set_sensitive(False)
        self.yes.connect("clicked", self.yes_clicked)
        answer_hbox.pack_start(self.yes)
        self.no = gtk.Button(label="No")
        self.no.set_sensitive(False)
        self.no.connect("clicked", self.no_clicked)
        answer_hbox.pack_start(self.no)
        
        action_vbox.pack_start(answer_hbox)
        
        self.play = gtk.Button(label="Play")
        self.play.set_sensitive(False)
        self.play.connect("clicked", self.play_clicked)
        action_vbox.pack_start(self.play)
        
        self.buy = gtk.Button(label="Buy")
        self.buy.set_sensitive(False)
        self.buy.connect("clicked", self.buy_clicked)
        action_vbox.pack_start(self.buy)
        
        self.discard = gtk.Button(label="Discard")
        self.discard.set_sensitive(False)
        self.discard.connect("clicked", self.discard_clicked)
        action_vbox.pack_start(self.discard)
        
        self.trash = gtk.Button(label="Trash")
        self.trash.set_sensitive(False)
        self.trash.connect("clicked", self.trash_clicked)
        action_vbox.pack_start(self.trash)
        
        self.actions = gtk.Label("Actions: 0")
        action_vbox.pack_start(self.actions)
        self.buys = gtk.Label("Buys: 0")
        action_vbox.pack_start(self.buys)
        self.money = gtk.Label("Money: 0")
        action_vbox.pack_start(self.money)
        
        main_container.pack1(action_vbox)
        
        play_area = gtk.VPaned()
        
        self.stacks = gtk.ListStore(gobject.TYPE_STRING, gobject.TYPE_INT, gobject.TYPE_INT)
        self.stacks_view = gtk.TreeView(self.stacks)
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn("Card", cell)
        self.stacks_view.append_column(tvcolumn)
        tvcolumn.set_attributes(cell, text=0)
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn("Cost", cell)
        self.stacks_view.append_column(tvcolumn)
        tvcolumn.set_attributes(cell, text=1)
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn("Qty", cell)
        self.stacks_view.append_column(tvcolumn)
        tvcolumn.set_attributes(cell, text=2)
        
        play_area.pack1(self.stacks_view)
        
        bottom_hbox = gtk.HBox()
        
        self.hand = gtk.ListStore(gobject.TYPE_STRING)
        self.hand_view = gtk.TreeView(self.hand)
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn("Card", cell)
        self.hand_view.append_column(tvcolumn)
        tvcolumn.set_attributes(cell, text=0)
        bottom_hbox.pack_start(self.hand_view)
        
        self.in_play = gtk.ListStore(gobject.TYPE_STRING)
        self.in_play_view = gtk.TreeView(self.in_play)
        cell = gtk.CellRendererText()
        tvcolumn = gtk.TreeViewColumn("Card", cell)
        self.in_play_view.append_column(tvcolumn)
        tvcolumn.set_attributes(cell, text=0)
        bottom_hbox.pack_start(self.in_play_view)
        
        play_area.pack2(bottom_hbox)
        
        main_container.pack2(play_area)

        window.add(main_container)
        window.show_all()
        window.connect("destroy", self.delete_event)
        
        self.communication_mutex = threading.Lock()
        self.communication_mutex.acquire()
    
    def delete_event(self, event):
        print "quitting"
        gobject.idle_add(gtk.main_quit)
        sys.exit(0)

    def set_stacks(self, stacks):
        print "set stacks"
        stacks.sort(key=lambda x: x.type.price) 
        for s in stacks:
            self.stacks.append((s.type.name, s.type.price, s.count))
        self.communication_mutex.release()
        print "/set stacks"
        
    def tell_stacks(self, stacks):
        print "tell stacks"
        gobject.idle_add(self.set_stacks, stacks)
        self.communication_mutex.acquire()
        print "/tell stacks"

    def set_hand(self, hand):
        self.hand.clear()
        print "set hand", hand
        for h in hand:
            print "set hand", h.name
            self.hand.append((h.name,))
        self.communication_mutex.release()

    def tell_hand(self, hand):
        print "tell hand", hand
        gobject.idle_add(self.set_hand, hand)
        self.communication_mutex.acquire();
            
    def tell_deck(self, hand):
        pass
        
    def set_stats(self, actions, buys, money):
        self.actions.set_text("Actions: %d"%actions)
        self.buys.set_text("Buys: %d"%buys)
        self.money.set_text("Money: %d"%money)

    def tell_stats(self, player):
        print "tell stats"
        gobject.idle_add(self.set_stats, player.actions, player.buys, player.money)

    def tell_buyphase(self):
        self.ask_yesno("Want to continue to buyphase?")
        
    def tell_reveal(self, player, card):
        # TODO: log
        if not card:
            print "WTF"
            return
        print player.name, "reveals", card.name

    def yes_clicked(self, *args):
        self.result = True
        self.communication_mutex.release()

    def no_clicked(self, *args):
        self.result = False
        self.communication_mutex.release()

    def ask_yesno_helper(self, message):
        self.question_label.set_text(message)
        self.yes.set_sensitive(True)
        self.no.set_sensitive(True)

    def ask_yesno_cleanup(self):
        self.question_label.set_text("")
        self.yes.set_sensitive(False)
        self.no.set_sensitive(False)

    def ask_buy(self):
        return self.ask_yesno("Do you want to buy something?")

    def ask_yesno(self, message):
        print "ask yesno", message
        gobject.idle_add(self.ask_yesno_helper, message)
        self.communication_mutex.acquire()
        gobject.idle_add(self.ask_yesno_cleanup)
        print "result is", self.result
        return self.result
        
    def ask_action(self):
        print "ask action"
        return self.ask_yesno("Do you want to play an action card?")
    
    def play_clicked(self, *args):
        pass

    def buy_clicked(self, *args):
        model, iter = self.stacks_view.get_selection().get_selected()
        self.result = model.get(iter, 0)[0]
        self.communication_mutex.release()

    def discard_clicked(self, *args):
        pass

    def trash_clicked(self, *args):
        pass
        
    def ask_which(self, choices, lalala):
        import random
        if not choices:
            return -1
        return random.randint(0, len(choices)-1)

    def ask_whichaction(self, actions):
        return self.ask_which(map(lambda a: a.name, actions), "Which action card do you want to play? (0 to stop playing actions)")
        
    def whichbuy_setup(self):
        self.buy.set_sensitive(True)
    
    def whichbuy_cleanup(self):
        self.buy.set_sensitive(False)

    def ask_whichbuy(self, options):
        choice = ""
        gobject.idle_add(self.whichbuy_setup)
        while choice not in map(lambda a: a.type.name, options):
            self.communication_mutex.acquire()
            choice = self.result
            print "got selection:", choice
        gobject.idle_add(self.whichbuy_cleanup)
        return map(lambda a: a.type.name, options).index(choice)
        
    def ask_whichgain(self, options):
        return self.ask_which(map(lambda a: a.type.name + " ($" + str(a.type.price) + ", " + str(a.count) + " left)", options), "Which card do you want to gain?")
        
    def ask_whichdiscard(self, cards, optional):
        return self.ask_which(map(lambda c: c.name, cards), "Which card do you want to discard?" + (" (0 to stop discarding)" if optional else ""))
        
    def ask_whichreaction(self, cards):
        return self.ask_which(map(lambda c: c.name, cards), "Which reaction do you want to use? (0 to stop responding)")
        
    def ask_whichtrash(self, cards, optional):
        return self.ask_which(map(lambda c: c.name, cards), "Which card do you want to trash?" + (" (0 to not trash anything)" if optional else ""))
        
    def ask_putdiscard(self):
        return self.ask_yesno("Do you want to put your deck into your discard pile?")
        
    def ask_whichvictorycard(self, options, cause):
        return self.ask_which(map(lambda c: c.name, options), "Which victory do you want to choose for " + cause.name +"?")
        
    def ask_keep(self, player, card):
        return self.ask_yesno("Can " + player.name + " keep " + card.name + "?")
        
    def ask_wantgain(self, card):
        return self.ask_yesno("Do you want to gain " + card.name + "?")

    def tell_attack(self, attacker, card):
        print attacker.name, "is attacking you with", card.name
        
    def tell_winner(self, winner):
        print winner, "has won the game!"
    
    def get_name(self):
        return self.name
        
    def tell_start_turn(self):
        print self.name + ", it's your turn!"
    
        