//
//  ECAppDelegate.h
//  Contribtastic
//
//  Created by Yann Ramin on 12/1/11.
//  Copyright (c) 2011 StackFoundry LLC. All rights reserved.
//

#import <Cocoa/Cocoa.h>

#import "ECUploadManager.h"

@interface ECAppDelegate : NSObject <NSApplicationDelegate>

@property (assign) IBOutlet NSWindow *window;
@property (assign) IBOutlet NSMenu *menu;
@property (retain) NSStatusItem *statusItem;
@property (retain) ECUploadManager *uploadManager;
- (IBAction)onQuit:(id)sender;
- (IBAction)scanNow:(id)sender;


@end
