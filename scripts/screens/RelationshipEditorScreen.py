from typing import Optional
from math import ceil
from random import choice

import i18n
import pygame.transform
import pygame_gui.elements
from pygame_gui.core import UIContainer

from scripts.cat.cats import Cat
from scripts.cat_relations.enums import RelType, RelTier, rel_type_tiers
from scripts.game_structure import image_cache, game, constants
from ..clan_package.settings import get_clan_setting
from scripts.clan_package.settings import switch_clan_setting
from scripts.game_structure.game.switches import (
    switch_set_value,
    Switch,
    switch_get_value,
)

from scripts.ui.elements.cat_list_display import UICatListDisplay
from ..ui.generate_button import get_button_dict, ButtonStyles
from ..ui.icon import Icon
from ..ui.elements.relation_display import UIRelationDisplay
from ..ui.elements.sprite_button import UISpriteButton
from ..ui.elements.image_button import UIImageButton
from ..ui.elements.surface_image_button import UISurfaceImageButton

from .Screens import Screens
from .enums import GameScreen

from ..ui.theme import get_text_box_theme
from ..events_module.text_adjust import shorten_text_to_fit
from ..ui.scale import ui_scale, ui_scale_dimensions, ui_scale_offset
from ..game_structure.screen_settings import MANAGER, screen
from ..ui.generate_box import get_box, BoxStyles
from ..ui.elements.text_box_tweaked import UITextBoxTweaked




class RelationshipEditorScreen(Screens):
    def __init__(self, name=None):
        super().__init__(name)
        self.all_relations = None
        self.the_cat = None
        self.back_button = None

        self.current_cat_elements = {}
        self.selected_cat_elements = {}

        self.info = None

        self.previous_cat_button = None
        self.next_cat_button = None
        self.conditions_background = None
        self.previous_cat = None
        self.next_cat = None
        self.the_cat = None
        self.selected_cat = None
        self.search_bar = None
        self.search_bar_image = None
        self.checkboxes = {}
        self.show_dead_checkbox = None
        self.rel_type_box = {}
        self.rel_type_buttons = {}
        self.rel_type_text = {}
        self.rel_change_inc = {}
        self.rel_change_dec = {}
        self.cat_buttons = []
        self.cat_display = None
        self.page = 1
        self.all_pages = 1
        self.sprite_buttons = {}
        self.relation_list_elements = {}
        self.allow_romance = True
        self.current_listed_cats = None
        self.previous_search_text = ""
        self.show_dead_text = None

    def handle_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_START_PRESS:
            self.mute_button_pressed(event)

            if event.ui_element in self.sprite_buttons.values():
                self.inspect_cat = event.ui_element.return_cat_object()
            if event.ui_element == self.back_button:
                self.change_screen(game.last_screen_forupdate)
            elif event.ui_element == self.previous_cat_button:
                if isinstance(Cat.fetch_cat(self.previous_cat), Cat):
                    switch_set_value(Switch.cat, self.previous_cat)
                    self.update_current_cat_info()
                    self.draw_info_block(self.the_cat, starting_pos=(50, 100))
                else:
                    print("invalid previous cat", self.previous_cat)
            elif event.ui_element == self.next_cat_button:
                if isinstance(Cat.fetch_cat(self.next_cat), Cat):
                    switch_set_value(Switch.cat, self.next_cat)
                    self.update_current_cat_info()
                    self.draw_info_block(self.the_cat, starting_pos=(50, 100))
                else:
                    print("invalid next cat", self.next_cat)

            elif event.ui_element == self.next_page:
                self.page += 1
                self.update_page()
            elif event.ui_element == self.previous_page:
                self.page -= 1
                self.update_page()
            elif event.ui_element == self.checkboxes["show_dead"]:
                switch_clan_setting("show dead relation")
                self.update_checkboxes()
                self.apply_cat_filter()
            elif event.ui_element == self.remove_cat:
                self.selected_cat = None
                self.update_selected_cat()


            elif event.ui_element == self.rel_change_inc["like_increase"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.LIKE
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_dec["like_decrease"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.LIKE,
                    decrease=True
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_inc["respect_increase"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.RESPECT
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_dec["respect_decrease"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.RESPECT,
                    decrease=True
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_inc["trust_increase"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.TRUST
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_dec["trust_decrease"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.TRUST,
                    decrease=True
                )
                self.update_current_cat_info(reset_selected_cat=False)


            elif event.ui_element == self.rel_change_inc["comfort_increase"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.COMFORT
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_dec["comfort_decrease"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.COMFORT,
                    decrease=True
                )
                self.update_current_cat_info(reset_selected_cat=False)


            elif event.ui_element == self.rel_change_inc["romance_increase"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.ROMANCE
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.rel_change_dec["romance_decrease"]:
                Cat.edit_relationship(
                    self.the_cat,
                    self.selected_cat,
                    self.allow_romance,
                    chosen_rel=RelType.ROMANCE,
                    decrease=True
                )
                self.update_current_cat_info(reset_selected_cat=False)

            elif event.ui_element == self.randomize_selected:
                self.selected_cat = self.random_cat()
                if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                    self.the_cat = self.random_cat()
                self.update_both()
            elif event.ui_element in self.cat_buttons:
                if event.ui_element.return_cat_object() not in (
                    self.the_cat,
                    self.selected_cat,
                ):
                    if (
                        pygame.key.get_mods() & pygame.KMOD_SHIFT
                        or not self.the_cat
                    ):
                        self.the_cat = event.ui_element.return_cat_object()
                    else:
                        self.selected_cat = event.ui_element.return_cat_object()
                    self.update_selected_cat()

    def update_checkboxes(self):
        # Remove all checkboxes
        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}
        self.checkboxes["show_dead"] = UIImageButton(
            ui_scale(pygame.Rect((34, 0), (34, 34))),
            "",
            object_id=(
                "@checked_checkbox"
                if get_clan_setting("show dead relation")
                else "@unchecked_checkbox"
            ),
            anchors={
                "left": "left",
                "left_target": self.search_bar_image,
                "top": "top",
                "top_target": self.search_bar_image
            },
        )
        self.show_dead_checkbox = UIImageButton(
            ui_scale(pygame.Rect((34, 0), (34, 34))),
            "",
            object_id="@buttonstyles_squoval",
            anchors={
                "left": "left",
                "left_target": self.search_bar_image,
                "top": "top",
                "top_target": self.search_bar_image
            },
        )
        self.show_dead_checkbox.hide()

    def screen_switches(self):
        super().screen_switches()
        self.show_mute_buttons()

        self.page = 1

        self.back_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 60), (105, 30))),
            "buttons.back",
            get_button_dict(ButtonStyles.SQUOVAL, (105, 30)),
            object_id="@buttonstyles_squoval",
            manager=MANAGER,
        )

        self.next_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((622, 25), (153, 30))),
            "buttons.next_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )
        self.previous_cat_button = UISurfaceImageButton(
            ui_scale(pygame.Rect((25, 25), (153, 30))),
            "buttons.previous_cat",
            get_button_dict(ButtonStyles.SQUOVAL, (153, 30)),
            object_id="@buttonstyles_squoval",
            sound_id="page_flip",
            manager=MANAGER,
        )

        self.the_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 95), (220, 370))),
            get_box(BoxStyles.ROUNDED_BOX, (220, 350)),
        )
        self.selected_cat_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((530, 95), (220, 370))),
            get_box(BoxStyles.ROUNDED_BOX, (220, 350)),
        )

        self.remove_cat = UISurfaceImageButton(
            ui_scale(pygame.Rect((-127, 380), (127, 30))),
            "buttons.remove_cat",
            get_button_dict(ButtonStyles.MENU_LEFT, (127, 30)),
            object_id="@buttonstyles_menu_left",
            manager=MANAGER,
            anchors={"right": "right", "right_target": self.selected_cat_frame},
        )
        self.randomize_selected = UISurfaceImageButton(
            ui_scale(pygame.Rect((-75, 30), (34, 34))),
            Icon.DICE,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
            sound_id="dice_roll",
            anchors={
                "right": "right",
                "bottom": "bottom",
                "right_target": self.selected_cat_frame,
                "bottom_target": self.remove_cat
            },
        )

        self.cat_list_frame = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((50, 470), (700, 150))),
            get_box(BoxStyles.ROUNDED_BOX, (700, 150)),
        )

        self.search_bar_image = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((55, 625), (118, 34))),
            pygame.image.load("resources/images/search_bar.png").convert_alpha(),
            manager=MANAGER,
        )
        self.search_bar = pygame_gui.elements.UITextEntryLine(
            ui_scale(pygame.Rect((60, 629), (115, 27))),
            object_id="#search_entry_box",
            placeholder_text="general.name_search",
            manager=MANAGER,
        )

        self.show_dead_text = pygame_gui.elements.UITextBox(
            "screens.relationship.show_dead_checkbox",
            ui_scale(pygame.Rect((100, 0), (100, 30))),
            object_id="#text_box_30_horizleft",
            anchors={
                "left": "left",
                "left_target": self.show_dead_checkbox,
                "top": "top"
            }
        )
        self.show_dead_text.disable()


        self.update_checkboxes()


        self.next_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((433, 619), (34, 34))),
            Icon.ARROW_RIGHT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )
        self.previous_page = UISurfaceImageButton(
            ui_scale(pygame.Rect((333, 619), (34, 34))),
            Icon.ARROW_LEFT,
            get_button_dict(ButtonStyles.ICON, (34, 34)),
            object_id="@buttonstyles_icon",
            manager=MANAGER,
        )


        self.update_list_cats()
        self.update_rel_choices()
        self.update_both()
        self.draw_info_block(self.the_cat, starting_pos=(50, 100))

    def random_cat(self):
        if self.selected_cat_list():
            random_list = [
                i for i in self.all_cats_list if i.ID not in self.selected_cat_list()
            ]
        else:
            random_list = self.all_cats_list
        return choice(random_list)

    def update_rel_choices(self):
        for ele in self.rel_type_buttons:
            self.rel_type_buttons[ele].kill()
        self.rel_type_buttons = {}
        for ele in self.rel_type_text:
            self.rel_type_text[ele].kill()
        self.rel_type_text = {}
        for ele in self.rel_change_inc:
            self.rel_change_inc[ele].kill()
        self.rel_change_inc = {}
        for ele in self.rel_change_dec:
            self.rel_change_dec[ele].kill()
        self.rel_change_dec = {}


        self.rel_type_buttons["rel_choices_frame"] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((275, 80), (252, 252))),
                get_box(BoxStyles.ROUNDED_BOX, (252, 252)),
            )

        self.rel_button_container = UIContainer(
                ui_scale(pygame.Rect((275, 80), (252, 252))),
                manager=MANAGER,
            )
        self.rel_type_box["like"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 36), (126, 36))),
            "Like",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
        )
        self.rel_change_inc["like_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 36), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                anchors={"right": "right", "right_target": self.rel_type_box["like"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["like_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,36), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["like"]},
                container=self.rel_button_container,
            )

        self.rel_type_box["respect"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 0), (126, 36))),
            "Respect",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
            anchors={"top_target": self.rel_type_box["like"]}
        )
        self.rel_change_inc["respect_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 0), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["respect"], "top_target": self.rel_type_box["like"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["respect_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,0), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["respect"], "top_target": self.rel_type_box["like"]},
                container=self.rel_button_container,
            )


        self.rel_type_box["trust"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 0), (126, 36))),
            "Trust",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
            anchors={"top_target": self.rel_type_box["respect"]}
        )
        self.rel_change_inc["trust_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 0), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["trust"], "top_target": self.rel_type_box["respect"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["trust_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,0), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["trust"], "top_target": self.rel_type_box["respect"]},
                container=self.rel_button_container,
            )


        self.rel_type_box["comfort"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, 0), (126, 36))),
            "Comfort",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 36))["normal"]},
            object_id="@buttonstyles_menu_middle",
            container=self.rel_button_container,
            manager=MANAGER,
            anchors={"top_target": self.rel_type_box["trust"]}
        )
        self.rel_change_inc["comfort_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 0), (48, 36))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 36)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["comfort"], "top_target": self.rel_type_box["trust"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["comfort_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,0), (48, 36))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 36)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["comfort"], "top_target": self.rel_type_box["trust"]},
                container=self.rel_button_container,
            )


        self.rel_type_box["romance"] = UISurfaceImageButton(
            ui_scale(pygame.Rect((63, -7), (126, 56))),
            "Romantic\nInterest",
            {"normal": get_button_dict(ButtonStyles.MENU_MIDDLE, (126, 42))["normal"]},
            object_id="@buttonstyles_menu_middle",
            text_layer_object_id="@buttonstyles_ladder_multiline",
            container=self.rel_button_container,
            manager=MANAGER,
            anchors={"top_target": self.rel_type_box["comfort"]},
            text_is_multiline=True,
        )
        self.rel_change_inc["romance_increase"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((124, 0), (48, 42))),
                "screens.relationship_editor.plus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_RIGHT, (48, 42)),
                object_id="@buttonstyles_profile_right",
                manager=MANAGER,
                anchors={"right": "right", "right_target": self.rel_type_box["romance"], "top_target": self.rel_type_box["comfort"]},
                container=self.rel_button_container,
            )
        self.rel_change_dec["romance_decrease"] = UISurfaceImageButton(
                ui_scale(pygame.Rect((-171,0), (48, 42))),
                "screens.relationship_editor.minus_icon_placeholder",
                get_button_dict(ButtonStyles.PROFILE_LEFT, (48, 42)),
                object_id="@buttonstyles_profile_left",
                manager=MANAGER,
                anchors={"left": "left", "left_target": self.rel_type_box["romance"], "top_target": self.rel_type_box["comfort"]},
                container=self.rel_button_container,
            )

        self.update_list_cats()

    def update_list_cats(self):
        self.all_cats_list = [
            i
            for i in Cat.all_cats_list
            if i.status.alive_in_player_clan
        ]
        self.all_cats = self.chunks(self.all_cats_list, 24)
        self.current_listed_cats = self.all_cats_list
        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )
        self.update_page()

    def update_page(self):
        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []
        if self.page > self.all_pages:
            self.page = self.all_pages
        elif self.page < 1:
            self.page = 1

        if self.page >= self.all_pages:
            self.next_page.disable()
        else:
            self.next_page.enable()

        if self.page <= 1:
            self.previous_page.disable()
        else:
            self.previous_page.enable()

        x = 65
        y = 485
        chunked_cats = self.chunks(self.current_listed_cats, 24)
        if chunked_cats:
            for cat in chunked_cats[self.page - 1]:
                if get_clan_setting("show fav") and cat.favourite:
                    _temp = pygame.transform.scale(
                        pygame.image.load(
                            f"resources/images/fav_marker.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((50, 50)),
                    )

                    self.cat_buttons.append(
                        pygame_gui.elements.UIImage(
                            ui_scale(pygame.Rect((x, y), (50, 50))), _temp
                        )
                    )

                self.cat_buttons.append(
                    UISpriteButton(
                        ui_scale(pygame.Rect((x, y), (50, 50))),
                        cat.sprite,
                        cat_object=cat,
                    )
                )
                x += 55
                if x > 700:
                    y += 55
                    x = 65




    def update_current_cat_info(self, reset_selected_cat=True):
        """Updates all elements with the current cat, as well as the selected cat.
        Called when the screen switched, and whenever the focused cat is switched"""
        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()

        (
            self.next_cat,
            self.previous_cat,
        ) = self.the_cat.determine_next_and_previous_cats(
            filter_func=(
                lambda cat: cat.age
                in ("newborn", "kitten", "juvenile", "adolescent", "young adult", "adult", "senior adult", "senior")
            )
        )
        (
            self.next_cat_button.disable()
            if self.next_cat == 0
            else self.next_cat_button.enable()
        )
        (
            self.previous_cat_button.disable()
            if self.previous_cat == 0
            else self.previous_cat_button.enable()
        )

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}


        self.current_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((100, 107), (100, 100))),
            pygame.transform.scale(
                self.the_cat.sprite, ui_scale_dimensions((100, 100))
            ),
        )

        if reset_selected_cat:
            self.selected_cat = None
        self.update_selected_cat()

    def update_selected_cat(self):
        """Updates all elements of the selected cat"""

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        if not isinstance(self.selected_cat, Cat):
            self.selected_cat = None
            return


        self.selected_cat_elements["image"] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((600, 107), (100, 100))),
            pygame.transform.scale(
                self.selected_cat.sprite, ui_scale_dimensions((100, 100))
            ),
        )


        self.draw_info_block(self.the_cat, starting_pos=(50, 100))
        self.draw_info_block(self.selected_cat, starting_pos=(550, 100))

    def update_both(self):
        """Updates both the current cat and selected cat info."""

        self.update_current_cat_info(
            reset_selected_cat=False
        )  # This will also refresh tab contents
        self.update_selected_cat()

    def draw_info_block(self, cat, starting_pos: tuple):
        if not cat:
            return

        self.the_cat = Cat.all_cats[switch_get_value(Switch.cat)]
        if not self.the_cat.inheritance:
            self.the_cat.create_inheritance_new_cat()


        other_cat = [Cat.fetch_cat(i) for i in self.selected_cat_list() if i != cat.ID]
        if other_cat:
            other_cat = other_cat[0]
        else:
            other_cat = None

        tag = str(starting_pos)

        x = starting_pos[0]
        y = starting_pos[1]

        self.selected_cat_elements["cat_image" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 50, y + 7), (100, 100))),
            pygame.transform.scale(cat.sprite, ui_scale_dimensions((100, 100))),
        )

        name = str(cat.name)
        short_name = shorten_text_to_fit(name, 62, 7)
        self.selected_cat_elements["name" + tag] = pygame_gui.elements.UILabel(
            ui_scale(pygame.Rect((x, y + 100), (200, 30))),
            short_name,
            object_id="#text_box_30_horizcenter",
        )
        self.selected_cat_elements["name" + tag].disable()

        # Gender
        if cat.genderalign == "female":
            gender_icon = image_cache.load_image(
                "resources/images/female_big.png"
            ).convert_alpha()
        elif cat.genderalign == "male":
            gender_icon = image_cache.load_image(
                "resources/images/male_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans female":
            gender_icon = image_cache.load_image(
                "resources/images/transfem_big.png"
            ).convert_alpha()
        elif cat.genderalign == "trans male":
            gender_icon = image_cache.load_image(
                "resources/images/transmasc_big.png"
            ).convert_alpha()
        else:
            # Everyone else gets the nonbinary icon
            gender_icon = image_cache.load_image(
                "resources/images/nonbi_big.png"
            ).convert_alpha()

        self.selected_cat_elements["gender" + tag] = pygame_gui.elements.UIImage(
            ui_scale(pygame.Rect((x + 160, y + 12), (25, 25))),
            pygame.transform.scale(gender_icon, ui_scale_dimensions((25, 25))),
        )

        related = False
        # MATE
        if other_cat and len(cat.mate) > 0 and other_cat.ID in cat.mate:
            self.selected_cat_elements["mate_icon" + tag] = pygame_gui.elements.UIImage(
                ui_scale(pygame.Rect((x + 14, y + 14), (22, 20))),
                pygame.transform.scale(
                    image_cache.load_image(
                        "resources/images/heart_big.png"
                    ).convert_alpha(),
                    ui_scale_dimensions((44, 40)),
                ),
            )
        elif other_cat:
            # FAMILY DOT
            # Only show family dot on cousins if first cousin mates are disabled.
            if get_clan_setting("first cousin mates"):
                check_cousins = False
            else:
                check_cousins = other_cat.is_cousin(cat)

            if (
                other_cat.is_uncle_aunt(cat)
                or cat.is_uncle_aunt(other_cat)
                or other_cat.is_grandparent(cat)
                or cat.is_grandparent(other_cat)
                or other_cat.is_parent(cat)
                or cat.is_parent(other_cat)
                or other_cat.is_sibling(cat)
                or check_cousins
            ):
                related = True
                self.selected_cat_elements[
                    "relation_icon" + tag
                ] = pygame_gui.elements.UIImage(
                    ui_scale(pygame.Rect((x + 14, y + 14), (18, 18))),
                    pygame.transform.scale(
                        image_cache.load_image(
                            "resources/images/dot_big.png"
                        ).convert_alpha(),
                        ui_scale_dimensions((18, 18)),
                    ),
                )


        col1 = i18n.t("general.moons_age", count=cat.moons)
        t = i18n.t(f"cat.personality.{cat.personality.trait}")
        if len(t) > 15:
            col1 += "\n" + t[:12] + "..."
        else:
            col1 += "\n" + t
        self.selected_cat_elements["col1" + tag] = pygame_gui.elements.UITextBox(
            col1,
            ui_scale(pygame.Rect((x + 21, y + 126), (90, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        self.selected_cat_elements["col1" + tag].disable()

        mates = False
        if len(cat.mate) > 0:
            col2 = i18n.t("general.has_a_mate")
            t = i18n.t(f"{cat.skills.skill_string(short=True)}")
            if len(t) > 15:
                col2 += "\n" + t[:12] + "..."
            else:
                col2 += "\n" + t
        else:
            col2 = i18n.t("general.mate_none")
            t = i18n.t(f"{cat.skills.skill_string(short=True)}")
            if len(t) > 15:
                col2 += "\n" + t[:12] + "..."
            else:
                col2 += "\n" + t

        self.selected_cat_elements["col2" + tag] = pygame_gui.elements.UITextBox(
            col2,
            ui_scale(pygame.Rect((x + 110, y + 126), (100, -1))),
            object_id="#text_box_22_horizleft_spacing_95",
            manager=MANAGER,
        )
        self.selected_cat_elements["col2" + tag].disable()

        # Relation info:
        if related and other_cat and not mates:
            relation = ""
            if cat.is_uncle_aunt(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.niece"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.nephew"
                else:
                    relation = "general.siblings_child"
            elif other_cat.is_uncle_aunt(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.aunt"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.uncle"
                else:
                    relation = "general.parents_sibling"
            elif other_cat.is_grandparent(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.grandmother"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.grandfather"
                else:
                    relation = "general.grandparent"
            elif cat.is_grandparent(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.granddaughter"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.grandson"
                else:
                    relation = "general.grandchild"
            elif other_cat.is_parent(cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.mother"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.father"
                else:
                    relation = "general.parent"
            elif cat.is_parent(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.daughter"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.son"
                else:
                    relation = "general.child"
            elif other_cat.is_sibling(cat) or cat.is_sibling(other_cat):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.sister"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.brother"
                else:
                    relation = "general.sibling"

                if other_cat.is_littermate(cat) or cat.is_littermate(other_cat):
                    relation = i18n.t(
                        "general.sibling_littermate", relation=i18n.t(relation)
                    )
            elif not get_clan_setting("first cousin mates") and other_cat.is_cousin(
                cat
            ):
                if other_cat.genderalign in ("female", "trans female"):
                    relation = "general.cousin_female"
                elif other_cat.genderalign in ("male", "trans male"):
                    relation = "general.cousin_male"
                else:
                    relation = "general.cousin_nb"

            self.selected_cat_elements[
                "col2_relation" + tag
            ] = pygame_gui.elements.UITextBox(
                i18n.t("general.related_text"),
                ui_scale(pygame.Rect((x + 110, -15), (80, -1))),
                starting_height=3,
                object_id="#text_box_22_horizleft_spacing_95",
                manager=MANAGER,
                anchors={"top_target": self.selected_cat_elements["col2" + tag]},
            )
            self.selected_cat_elements["col2_relation" + tag].set_tooltip(
                text=i18n.t(relation)
            )
            self.selected_cat_elements["col2_relation" + tag].tool_tip_delay = 0
            self.selected_cat_elements["col2_relation" + tag].disable()

        # ------------------------------------------------------------------------------------------------------------ #
        # RELATION BARS

        # Keep a list of all the relations
        if constants.CONFIG["sorting"]["sort_by_rel_total"]:
            self.all_relations = sorted(
                self.the_cat.relationships.values(),
                key=lambda x: x.total_abs_relationship_value,
                reverse=True,
            )
        else:
            self.all_relations = list(self.the_cat.relationships.values()).copy()

        if other_cat:
            name = str(cat.name)
            short_name = shorten_text_to_fit(name, 68, 11)

            self.selected_cat_elements[
                f"relation_heading{tag}"
            ] = pygame_gui.elements.UILabel(
                ui_scale(pygame.Rect((x + 20, y + 160), (160, -1))),
                "screens.relationship_editor.cat_feelings",
                object_id="#text_box_22_horizcenter",
                text_kwargs={"name": short_name, "m_c": cat},
            )

            if other_cat.ID in cat.relationships:
                the_relationship = cat.relationships[other_cat.ID]
            else:
                the_relationship = cat.create_one_relationship(other_cat)

            # ROMANTIC LOVE
            # CHECK AGE DIFFERENCE
            same_age = the_relationship.cat_to.age == cat.age
            both_adult = (
                cat.age.can_have_mate() and the_relationship.cat_to.age.can_have_mate()
            )
            check_age = both_adult or same_age

            # If they are not both adults, or the same age, OR they are related, don't display any romantic affection,
            # even if they somehow have some. They should not be able to get any, but it never hurts to check.
            if not check_age or related:
                allow_romance = False
                self.rel_change_inc["romance_increase"].disable()
                self.rel_change_dec["romance_decrease"].disable()
                # Print, just for bug checking. Again, they should not be able to get love towards their relative.
                if the_relationship.romance and related:
                    print(
                        f"WARNING: {cat.name} has {the_relationship.romance} romantic love towards their relative, {the_relationship.cat_to.name}"
                    )
            else:
                allow_romance = True
                self.rel_change_inc["romance_increase"].enable()
                self.rel_change_dec["romance_decrease"].enable()

            self.selected_cat_elements[f"display{tag}"] = UIRelationDisplay(
                position=(x + 50, 0),
                relationship=the_relationship,
                romance=allow_romance,
                manager=MANAGER,
                anchors={
                    "top_target": self.selected_cat_elements[f"relation_heading{tag}"]
                },
            )


    def apply_cat_filter(self, search_text=""):
        # Filter for dead or empty cats
        self.filtered_cats = self.all_relations
        if not get_clan_setting("show dead relation"):
            self.filtered_cats = list(
                filter(lambda rel: not rel.cat_to.dead, self.filtered_cats)
            )
        # Filter for search
        search_cats = []
        if search_text.strip() != "":
            for cat in self.filtered_cats:
                if search_text.lower() in str(cat.cat_to.name).lower():
                    search_cats.append(cat)
            self.filtered_cats = search_cats

    def selected_cat_list(self):
        output = []
        if self.the_cat:
            output.append(self.the_cat.ID)
        if self.selected_cat:
            output.append(self.selected_cat.ID)

        return output

    def update_search_cats(self, search_text):
        """Run this function when the search text changes, or when the screen is switched to."""
        self.current_listed_cats = []
        Cat.sort_cats(self.all_cats_list)

        search_text = search_text.strip()
        if search_text not in (""):
            for cat in self.all_cats_list:
                if search_text.lower() in str(cat.name).lower():
                    self.current_listed_cats.append(cat)
        else:
            self.current_listed_cats = self.all_cats_list.copy()

        self.all_pages = (
            int(ceil(len(self.current_listed_cats) / 24.0))
            if len(self.current_listed_cats) > 24
            else 1
        )

        Cat.ordered_cat_list = self.current_listed_cats
        self.update_page()
        self.apply_cat_filter()

    def exit_screen(self):
        self.the_cat = None
        self.selected_cat = None

        for ele in self.checkboxes:
            self.checkboxes[ele].kill()
        self.checkboxes = {}

        self.show_dead_text.kill()
        del self.show_dead_text

        for ele in self.rel_type_buttons:
            self.rel_type_buttons[ele].kill()
        self.rel_type_buttons = {}

        for ele in self.rel_type_box:
            self.rel_type_box[ele].kill()
        self.rel_type_box = {}

        for ele in self.rel_change_inc:
            self.rel_change_inc[ele].kill()
        self.rel_change_inc = {}
        for ele in self.rel_change_dec:
            self.rel_change_dec[ele].kill()
        self.rel_change_dec = {}

        for cat in self.cat_buttons:
            cat.kill()
        self.cat_buttons = []

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.previous_cat_button.kill()
        del self.previous_cat_button
        self.next_cat_button.kill()
        del self.next_cat_button
        self.back_button.kill()
        del self.back_button
        self.the_cat_frame.kill()
        del self.the_cat_frame
        self.selected_cat_frame.kill()
        del self.selected_cat_frame
        self.cat_list_frame.kill()
        del self.cat_list_frame
        self.remove_cat.kill()
        del self.remove_cat
        self.next_page.kill()
        del self.next_page
        self.previous_page.kill()
        del self.previous_page
        self.randomize_selected.kill()
        del self.randomize_selected
        self.search_bar_image.kill()
        del self.search_bar_image
        self.search_bar.kill()
        del self.search_bar

        for ele in self.current_cat_elements:
            self.current_cat_elements[ele].kill()
        self.current_cat_elements = {}

        for ele in self.selected_cat_elements:
            self.selected_cat_elements[ele].kill()
        self.selected_cat_elements = {}

        self.checkboxes = {}
        self.show_dead_checkbox.kill()
        del self.show_dead_checkbox

    def on_use(self):
        super().on_use()
        # Only update the positions if the search text changes
        if self.search_bar.is_focused and self.search_bar.get_text() == "name search":
            self.search_bar.set_text("")
        if self.search_bar.get_text() != self.previous_search_text:
            self.update_search_cats(self.search_bar.get_text())
            self.apply_cat_filter(self.search_bar.get_text())
        self.previous_search_text = self.search_bar.get_text()