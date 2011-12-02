//
//  ECAppDelegate.m
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import "ECAppDelegate.h"

@implementation ECAppDelegate

@synthesize window = _window;
@synthesize menu = _menu;
@synthesize statusItem = _statusItem;

- (void)applicationDidFinishLaunching:(NSNotification *)aNotification
{
    NSStatusBar *bar = [NSStatusBar systemStatusBar];
    _statusItem = [bar statusItemWithLength:NSVariableStatusItemLength];
    [_statusItem setTitle: NSLocalizedString(@"EC",@"")];
    [_statusItem setHighlightMode:YES];
    [_statusItem setMenu:_menu];
}

@end
