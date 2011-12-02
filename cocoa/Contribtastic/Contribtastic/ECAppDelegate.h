//
//  ECAppDelegate.h
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import <Cocoa/Cocoa.h>

@interface ECAppDelegate : NSObject <NSApplicationDelegate>

@property (assign) IBOutlet NSWindow *window;
@property (assign) IBOutlet NSMenu *menu;
@property (retain) NSStatusItem *statusItem;
- (IBAction)onQuit:(id)sender;

@end
